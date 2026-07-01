# app.py
from flask import Flask
from extensions import mysql

app = Flask(__name__)

# Application Cryptographic Token
app.secret_key = 'super_secure_school_zone_token_xyz'

# Database Engine Properties
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@meddy4BR'
app.config['MYSQL_DB'] = 'school_zone_database'

# Instantiate Global Connections
mysql.init_app(app)

# Register Segmented Application Blueprints
from blueprints.public import public_bp
from blueprints.auth import auth_bp
from blueprints.dashbod import dashbod_bp
from blueprints.user import user_bp
from blueprints.violation import violation_bp
from blueprints.invoice_details import invoice_bp
from blueprints.report import report_bp
from blueprints.settings import settings_bp
from blueprints.communication import comms_bp

app.register_blueprint(public_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(dashbod_bp)
app.register_blueprint(user_bp)
app.register_blueprint(violation_bp)
app.register_blueprint(invoice_bp)
app.register_blueprint(report_bp)
app.register_blueprint(settings_bp)
app.register_blueprint(comms_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5000)