from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    migrate.init_app(app, db)

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

        from app.models import Customer, Product, Payment

        db.create_all()

    return app