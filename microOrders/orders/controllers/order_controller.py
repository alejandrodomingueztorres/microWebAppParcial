from flask import Blueprint, request, jsonify, session
from orders.models.order_model import Order, OrderItem
from db.db import db
from products_client import get_product, adjust_inventory, ProductsServiceUnavailable

order_controller = Blueprint('order_controller', __name__)


@order_controller.route('/api/orders', methods=['GET'])
def get_all_orders():
    if 'username' not in session or 'email' not in session:
        return jsonify({'message': 'No hay sesion de usuario valida'}), 401
    orders = Order.query.filter_by(user_email=session['email']).order_by(Order.created_at.desc()).all()
    return jsonify([o.to_dict() for o in orders])


@order_controller.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    if 'username' not in session or 'email' not in session:
        return jsonify({'message': 'No hay sesion de usuario valida'}), 401
    order = Order.query.get(order_id)
    if not order:
        return jsonify({'message': 'Orden no encontrada'}), 404
    return jsonify(order.to_dict(include_items=True))


@order_controller.route('/api/orders', methods=['POST'])
def create_order():
    # a) sesion valida
    user_name = session.get('username')
    user_email = session.get('email')
    if not user_name or not user_email:
        return jsonify({'message': 'No hay sesion de usuario valida'}), 401

    data = request.get_json(silent=True) or {}
    products = data.get('products')
    if not products or not isinstance(products, list):
        return jsonify({'message': 'Informacion de productos invalida'}), 400
    for line in products:
        if not isinstance(line, dict) or 'product_id' not in line or 'quantity' not in line \
           or not isinstance(line['quantity'], (int, float)) or line['quantity'] <= 0:
            return jsonify({'message': 'Informacion de productos invalida'}), 400

    # b) consultar precio/existencias + c) verificar disponibilidad de TODAS las lineas
    order_lines = []
    try:
        for line in products:
            product_id, quantity = int(line['product_id']), int(line['quantity'])
            product = get_product(product_id)
            if product is None:
                return jsonify({'message': f'El producto {product_id} no existe'}), 404
            if product['quantity'] < quantity:
                return jsonify({'message': f"Inventario insuficiente para el producto {product_id}",
                                 'available': product['quantity'], 'requested': quantity}), 409
            order_lines.append({'product_id': product_id, 'quantity': quantity,
                                 'unit_price': product['price']})
    except ProductsServiceUnavailable as e:
        return jsonify({'message': f'Servicio de productos no disponible: {e}'}), 500

    # d) calcular el total
    total = sum(l['quantity'] * l['unit_price'] for l in order_lines)

    # e) actualizar inventario, con rollback si algo falla a mitad de camino
    applied = []
    try:
        for l in order_lines:
            ok, status_code, body = adjust_inventory(l['product_id'], l['quantity'])
            if not ok:
                _rollback_inventory(applied)
                if status_code == 409:
                    return jsonify({'message': f"Inventario insuficiente para el producto {l['product_id']}", **body}), 409
                if status_code == 404:
                    return jsonify({'message': f"El producto {l['product_id']} no existe"}), 404
                return jsonify({'message': 'Error actualizando inventario'}), 500
            applied.append(l)
    except ProductsServiceUnavailable as e:
        _rollback_inventory(applied)
        return jsonify({'message': f'Servicio de productos no disponible: {e}'}), 500

    # f) crear la orden + items y persistir
    try:
        new_order = Order(user_name=user_name, user_email=user_email, total=total)
        db.session.add(new_order)
        db.session.flush()
        for l in order_lines:
            db.session.add(OrderItem(order_id=new_order.id, product_id=l['product_id'],
                                      quantity=l['quantity'], unit_price=l['unit_price'],
                                      subtotal=l['quantity'] * l['unit_price']))
        db.session.commit()
    except Exception:
        db.session.rollback()
        _rollback_inventory(order_lines)
        return jsonify({'message': 'Error interno creando la orden'}), 500

    return jsonify({'message': 'Orden creada exitosamente',
                     'order': new_order.to_dict(include_items=True)}), 201


def _rollback_inventory(lines):
    for l in lines:
        try:
            adjust_inventory(l['product_id'], -l['quantity'])
        except ProductsServiceUnavailable:
            print(f"[microOrders] ALERTA: no se pudo revertir inventario del producto {l['product_id']}")
