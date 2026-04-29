from datetime import datetime
from app import db

class Customer(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(20), unique=True, nullable=False)

    email = db.Column(db.String(100))

    reg_date = db.Column(db.DateTime, default=datetime.now)


class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    product_name = db.Column(db.String(100), nullable=False)

    product_code = db.Column(db.String(50), unique=True)

    price = db.Column(db.Float, nullable=False)

    stock = db.Column(db.Integer, default=0)


class Payment(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    ref_number = db.Column(db.String(50), unique=True)

    customer_id = db.Column(
        db.Integer,
        db.ForeignKey('customer.id')
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey('product.id')
    )

    amount = db.Column(db.Float, nullable=False)

    method = db.Column(db.String(50))

    timestamp = db.Column(
        db.DateTime,
        default=datetime.now
    )