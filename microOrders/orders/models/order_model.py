from datetime import datetime
from db.db import db


class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(255), nullable=False)
    user_email = db.Column(db.String(255), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='CONFIRMED')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan', lazy=True)

    def __init__(self, user_name, user_email, total, status='CONFIRMED'):
        self.user_name = user_name
        self.user_email = user_email
        self.total = total
        self.status = status

    def to_dict(self, include_items=False):
        data = {
            'id': self.id, 'user_name': self.user_name, 'user_email': self.user_email,
            'total': float(self.total), 'status': self.status,
            'created_at': self.created_at.isoformat(),
        }
        if include_items:
            data['items'] = [item.to_dict() for item in self.items]
        return data


class OrderItem(db.Model):
    __tablename__ = 'order_items'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    subtotal = db.Column(db.Numeric(10, 2), nullable=False)

    def __init__(self, order_id, product_id, quantity, unit_price, subtotal):
        self.order_id = order_id
        self.product_id = product_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.subtotal = subtotal

    def to_dict(self):
        return {'id': self.id, 'product_id': self.product_id, 'quantity': self.quantity,
                'unit_price': float(self.unit_price), 'subtotal': float(self.subtotal)}
