from db.db import db
 
 
class Product(db.Model):
    __tablename__ = 'products'
 
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
 
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
 
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': float(self.price),
            'quantity': self.quantity,
        }

