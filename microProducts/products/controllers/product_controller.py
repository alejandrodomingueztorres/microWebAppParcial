from flask import Blueprint, request, jsonify
from products.models.product_model import Product
from db.db import db

product_controller = Blueprint('product_controller', __name__)


@product_controller.route('/api/products', methods=['GET'])
def get_products():
    return jsonify([p.to_dict() for p in Product.query.all()])


@product_controller.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    return jsonify(product.to_dict())


@product_controller.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json(silent=True) or {}
    if 'name' not in data or 'price' not in data or 'quantity' not in data:
        return jsonify({'message': 'Informacion de producto invalida'}), 400

    new_product = Product(name=data['name'], price=data['price'], quantity=data['quantity'])
    db.session.add(new_product)
    db.session.commit()
    return jsonify({'message': 'Product created successfully', 'id': new_product.id}), 201


@product_controller.route('/api/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    data = request.get_json(silent=True) or {}
    product.name = data.get('name', product.name)
    product.price = data.get('price', product.price)
    product.quantity = data.get('quantity', product.quantity)
    db.session.commit()
    return jsonify({'message': 'Product updated successfully'})


@product_controller.route('/api/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404
    db.session.delete(product)
    db.session.commit()
    return jsonify({'message': 'Product deleted successfully'})


@product_controller.route('/api/products/<int:product_id>/inventory', methods=['PUT'])
def update_inventory(product_id):
    """
    Body: {"quantity": N}
      N > 0 -> descuenta N unidades (venta, valida 409 si no alcanza)
      N < 0 -> repone |N| unidades (usado por microOrders para revertir
               una reserva cuando una orden falla a mitad de camino)
    """
    product = Product.query.get(product_id)
    if not product:
        return jsonify({'message': 'Producto no encontrado'}), 404

    data = request.get_json(silent=True) or {}
    delta = data.get('quantity')
    if delta is None or not isinstance(delta, (int, float)):
        return jsonify({'message': 'Cantidad invalida'}), 400
    delta = int(delta)

    if delta > 0 and product.quantity < delta:
        return jsonify({'message': 'Inventario insuficiente',
                         'available': product.quantity, 'requested': delta}), 409

    product.quantity -= delta
    db.session.commit()
    return jsonify(product.to_dict()), 200
