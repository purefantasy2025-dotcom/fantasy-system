from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # create qr folder
    if not os.path.exists('app/static/qrcodes'):
        os.makedirs('app/static/qrcodes')

    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.customers import customers_bp
    from app.routes.products import products_bp
    from app.routes.payments import payments_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(products_bp)
    app.register_blueprint(payments_bp)

    with app.app_context():
        from app.models import Product
        db.create_all()

        if Product.query.count() == 0:
            p1 = Product(product_name="Laptop HP", product_code="HP001", price=1200000, stock=10)
            p2 = Product(product_name="Samsung", product_code="SAM002", price=650000, stock=25)

            db.session.add_all([p1, p2])
            db.session.commit()

    return app