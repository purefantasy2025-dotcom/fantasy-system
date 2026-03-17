from flask import Flask, render_template_string, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import qrcode
import os
import io

# -----------------------------
# Flask & Configuration
# -----------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ase_web_enterprise.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "fantasy_enterprise_key_2026"

db = SQLAlchemy(app)

# Hakikisha folder la static lipo
if not os.path.exists('static/qrcodes'):
    os.makedirs('static/qrcodes')

# -----------------------------
# DATABASE MODELS
# -----------------------------
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(100))
    reg_date = db.Column(db.DateTime, default=datetime.now)
    payments = db.relationship('Payment', backref='customer', lazy=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    product_code = db.Column(db.String(50), unique=True)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    payments = db.relationship('Payment', backref='product', lazy=True)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ref_number = db.Column(db.String(50), unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    method = db.Column(db.String(50))
    timestamp = db.Column(db.DateTime, default=datetime.now)

# Initialize Database
with app.app_context():
    db.create_all()
    if Product.query.count() == 0:
        p1 = Product(product_name="Laptop HP", product_code="HP001", price=1200000, stock=10)
        p2 = Product(product_name="Smartphone Samsung", product_code="SAM002", price=650000, stock=25)
        p3 = Product(product_name="Office Chair", product_code="CHR003", price=150000, stock=50)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

# -----------------------------
# CSS
# -----------------------------
BASE_STYLE = """
<style>
    :root { --primary: #1e272e; --accent: #05c46b; --bg: #f1f2f6; --text: #2f3542; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: var(--bg); margin: 0; color: var(--text); }
    .sidebar { width: 250px; background: var(--primary); position: fixed; height: 100%; color: white; padding-top: 20px; box-shadow: 2px 0 5px rgba(0,0,0,0.2); }
    .sidebar h2 { text-align: center; color: var(--accent); font-size: 24px; margin-bottom: 30px; letter-spacing: 2px; }
    .sidebar a { display: block; padding: 15px 25px; color: #dcdde1; text-decoration: none; border-left: 4px solid transparent; transition: 0.3s; }
    .sidebar a:hover { background: #2f3542; color: white; border-left: 4px solid var(--accent); }
    .sidebar a.active { background: #2f3542; border-left: 4px solid var(--accent); color: white; }
    .main-content { margin-left: 250px; padding: 40px; }
    .header { background: white; padding: 15px 40px; margin-left: 250px; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    .stat-container { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
    .stat-card { background: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border-bottom: 4px solid var(--accent); }
    .stat-card h3 { margin: 0; font-size: 14px; color: #7f8c8d; text-transform: uppercase; }
    .stat-card p { margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: var(--primary); }
    .data-table { width: 100%; border-collapse: collapse; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .data-table th { background: #f8f9fa; padding: 15px; text-align: left; font-size: 13px; color: #7f8c8d; border-bottom: 2px solid #eee; }
    .data-table td { padding: 15px; border-bottom: 1px solid #eee; font-size: 14px; }
    .data-table tr:hover { background: #fcfcfc; }
    .btn { padding: 10px 20px; border: none; border-radius: 6px; cursor: pointer; font-weight: 600; text-decoration: none; display: inline-block; transition: 0.2s; }
    .btn-primary { background: var(--accent); color: white; }
    .btn-primary:hover { background: #04aa5d; }
    .btn-warning { background: #f39c12; color: white; }
    .form-box { background: white; padding: 30px; border-radius: 12px; max-width: 600px; box-shadow: 0 5px 15px rgba(0,0,0,0.08); }
    input, select { width: 100%; padding: 12px; margin: 10px 0 20px 0; border: 1px solid #ddd; border-radius: 6px; font-size: 14px; }
    .flash-msg { padding: 15px; background: #d4edda; color: #155724; border-radius: 6px; margin-bottom: 20px; }
</style>
"""

LAYOUT_START = f"""
<!DOCTYPE html>
<html lang="sw">
<head>
    <meta charset="UTF-8">
    <title>Fantasy ENTERPRISE WEB</title>
    {BASE_STYLE}
</head>
<body>
    <div class="sidebar">
        <h2>Fantasy WEB</h2>
        <a href="{{{{ url_for('dashboard') }}}}">🏠 Dashboard Summary</a>
        <a href="{{{{ url_for('show_customers') }}}}">👥 Customer Profiles</a>
        <a href="{{{{ url_for('show_products') }}}}">📦 Inventory Items</a>
        <a href="{{{{ url_for('show_payments') }}}}">💰 Payment Records</a>
        <a href="{{{{ url_for('login') }}}}">🚪 Logout System</a>
    </div>
    <div class="header">
        <div class="user-info">Logged in as: <strong>Admin</strong></div>
        <div class="date-info">{datetime.now().strftime('%d %B, %Y')}</div>
    </div>
    <div class="main-content">
        {{% with messages = get_flashed_messages() %}}
            {{% if messages %}}
                {{% for msg in messages %}}
                    <div class="flash-msg">{{{{ msg }}}}</div>
                {{% endfor %}}
            {{% endif %}}
        {{% endwith %}}
"""

LAYOUT_END = "</div></body></html>"

# -----------------------------
# ROUTES (login, dashboard, customers, payments)
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            return redirect(url_for('dashboard'))
        flash("Mtumiaji au Password si sahihi!")
    return render_template_string(f"""
    <!DOCTYPE html>
    <html><head><title>Login | Fantasy</title>{BASE_STYLE}</head>
    <body style="display:flex; align-items:center; justify-content:center; height:100vh; background: #1e272e;">
        <div class="form-box" style="width:350px;">
            <h2 style="text-align:center;">Fantasy ENTERPRISE</h2>
            <p style="text-align:center; color:gray;">Sign in to manage system</p>
            <form method="POST">
                <label>Username</label><input type="text" name="username" required>
                <label>Password</label><input type="password" name="password" required>
                <button class="btn btn-primary" style="width:100%;">ACCESS SYSTEM</button>
            </form>
            {{% with messages = get_flashed_messages() %}}
                {{% if messages %}}
                    <p style="color:red; text-align:center;">{{{{ messages[0] }}}}</p>
                {{% endif %}}
            {{% endwith %}}
        </div>
    </body></html>
    """)

@app.route('/')
@app.route('/dashboard')
def dashboard():
    total_c = Customer.query.count()
    total_p = db.session.query(db.func.sum(Payment.amount)).scalar() or 0
    total_stock = db.session.query(db.func.sum(Product.stock)).scalar() or 0
    recent_payments = Payment.query.order_by(Payment.timestamp.desc()).limit(5).all()
    html = LAYOUT_START + """
    <h1>Mwanzo - Fantasy Overview</h1>
    <div class="stat-container">
        <div class="stat-card"><h3>Total Customers</h3><p>{{ total_c }}</p></div>
        <div class="stat-card"><h3>Revenue (TZS)</h3><p>{{ "{:,.2f}".format(total_p) }}</p></div>
        <div class="stat-card"><h3>Inventory Stock</h3><p>{{ total_stock }} Items</p></div>
    </div>
    <h2>Recent Transactions</h2>
    <table class="data-table">
        <tr><th>Ref ID</th><th>Mteja</th><th>Kiasi</th><th>Muda</th></tr>
        {% for pay in recent_payments %}
        <tr>
            <td><strong>{{ pay.ref_number }}</strong></td>
            <td>{{ pay.customer.name }}</td>
            <td>TZS {{ "{:,.0f}".format(pay.amount) }}</td>
            <td>{{ pay.timestamp.strftime('%H:%M %p') }}</td>
        </tr>
        {% endfor %}
    </table>
    """ + LAYOUT_END
    return render_template_string(html, total_c=total_c, total_p=total_p, total_stock=total_stock, recent_payments=recent_payments)

# -----------------------------
# CUSTOMERS
# -----------------------------
@app.route('/customers', methods=['GET', 'POST'])
def show_customers():
    if request.method == 'POST':
        try:
            name = request.form['name']
            phone = request.form['phone']
            email = request.form['email']
            db.session.add(Customer(name=name, phone=phone, email=email))
            db.session.commit()
            flash("Mteja mpya amesajiliwa!")
        except:
            flash("Makosa: Huenda namba ya simu tayari ipo!")
        return redirect(url_for('show_customers'))

    customers = Customer.query.all()
    html = LAYOUT_START + """
    <h1>Management ya Wateja</h1>
    <div style="display: flex; gap: 30px;">
        <div style="flex: 2;">
            <table class="data-table">
                <tr><th>ID</th><th>Jina</th><th>Simu</th><th>Email</th><th>Action</th></tr>
                {% for c in customers %}
                <tr>
                    <td>#{{ c.id }}</td>
                    <td>{{ c.name }}</td>
                    <td>{{ c.phone }}</td>
                    <td>{{ c.email }}</td>
                    <td><a href="{{ url_for('get_qr', type='cust', id=c.id) }}" class="btn btn-warning" style="font-size:11px;">GET QR</a></td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div style="flex: 1;">
            <div class="form-box">
                <h3>Sajili Mteja Mpya</h3>
                <form method="POST">
                    <label>Jina Kamili</label><input type="text" name="name" required>
                    <label>Namba ya Simu</label><input type="text" name="phone" required>
                    <label>Barua Pepe</label><input type="email" name="email">
                    <button class="btn btn-primary" style="width:100%;">HIFADHI MTEJA</button>
                </form>
            </div>
        </div>
    </div>
    """ + LAYOUT_END
    return render_template_string(html, customers=customers)

# -----------------------------
# PAYMENTS
# -----------------------------
@app.route('/payments', methods=['GET', 'POST'])
def show_payments():
    if request.method == 'POST':
        cid = request.form['customer_id']
        pid = request.form['product_id']
        amt = float(request.form['amount'])
        mthd = request.form['method']
        ref = f"FNT-{datetime.now().strftime('%M%S%f')[:7]}"
        new_pay = Payment(ref_number=ref, customer_id=cid, product_id=pid, amount=amt, method=mthd)
        db.session.add(new_pay)
        db.session.commit()
        flash(f"Malipo yamekamilika! Ref: {ref}")
        return redirect(url_for('show_payments'))

    payments = Payment.query.order_by(Payment.timestamp.desc()).all()
    customers = Customer.query.all()
    products = Product.query.all()
    html = LAYOUT_START + """
    <h1>Miamala na Risiti</h1>
    <div style="display: flex; gap: 30px;">
        <div style="flex: 2;">
            <table class="data-table">
                <tr><th>Ref</th><th>Mteja</th><th>Bidhaa</th><th>Kiasi</th><th>Muda</th></tr>
                {% for p in payments %}
                <tr>
                    <td><strong>{{ p.ref_number }}</strong></td>
                    <td>{{ p.customer.name }}</td>
                    <td>{{ p.product.product_name }}</td>
                    <td>{{ "{:,.0f}".format(p.amount) }}</td>
                    <td>{{ p.timestamp.strftime('%Y-%m-%d %H:%M') }}</td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div style="flex: 1;">
            <div class="form-box">
                <h3>Tengeneza Malipo</h3>
                <form method="POST">
                    <label>Chagua Mteja</label>
                    <select name="customer_id">{% for c in customers %}<option value="{{ c.id }}">{{ c.name }}</option>{% endfor %}</select>
                    <label>Chagua Bidhaa</label>
                    <select name="product_id">{% for p in products %}<option value="{{ p.id }}">{{ p.product_name }} (TZS {{ p.price }})</option>{% endfor %}</select>
                    <label>Kiasi Kinacholipwa</label><input type="number" name="amount" required>
                    <label>Njia ya Malipo</label><select name="method"><option>CASH</option><option>MPESA</option><option>BANK</option></select>
                    <button class="btn btn-primary" style="width:100%;">KAMILISHA MALIPO</button>
                </form>
            </div>
        </div>
    </div>
    """ + LAYOUT_END
    return render_template_string(html, payments=payments, customers=customers, products=products)

# -----------------------------
# PRODUCTS (Add/Delete)
# -----------------------------
@app.route('/products', methods=['GET', 'POST'])
def show_products():
    if request.method == 'POST':
        if 'add_product' in request.form:
            pname = request.form['product_name']
            pcode = request.form['product_code']
            price = float(request.form['price'])
            stock = int(request.form['stock'])
            db.session.add(Product(product_name=pname, product_code=pcode, price=price, stock=stock))
            db.session.commit()
            flash("Bidhaa mpya imeongezwa!")
        elif 'delete_id' in request.form:
            pid = int(request.form['delete_id'])
            prod = Product.query.get(pid)
            if prod:
                db.session.delete(prod)
                db.session.commit()
                flash(f"Bidhaa {prod.product_name} imefutwa!")
        return redirect(url_for('show_products'))

    products = Product.query.all()
    html = LAYOUT_START + """
    <h1>Fantasy Inventory - Bidhaa</h1>
    <div style="display:flex; gap:30px;">
        <div style="flex:2;">
            <table class="data-table">
                <tr><th>ID</th><th>Jina la Bidhaa</th><th>Code</th><th>Bei</th><th>Stock</th><th>Actions</th></tr>
                {% for p in products %}
                <tr>
                    <td>#{{ p.id }}</td>
                    <td>{{ p.product_name }}</td>
                    <td>{{ p.product_code }}</td>
                    <td>{{ "{:,.0f}".format(p.price) }}</td>
                    <td>{{ p.stock }}</td>
                    <td>
                        <form method="POST" style="display:inline;">
                            <input type="hidden" name="delete_id" value="{{ p.id }}">
                            <button class="btn btn-warning" type="submit" onclick="return confirm('Unataka kufuta bidhaa hii?')">DELETE</button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
        <div style="flex:1;">
            <div class="form-box">
                <h3>Add Bidhaa Mpya</h3>
                <form method="POST">
                    <input type="hidden" name="add_product" value="1">
                    <label>Jina la Bidhaa</label><input type="text" name="product_name" required>
                    <label>Product Code</label><input type="text" name="product_code" required>
                    <label>Bei (TZS)</label><input type="number" name="price" required>
                    <label>Stock</label><input type="number" name="stock" required>
                    <button class="btn btn-primary" style="width:100%;">ONgeza Bidhaa</button>
                </form>
            </div>
        </div>
    </div>
    """ + LAYOUT_END
    return render_template_string(html, products=products)

# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # PORT inatolewa na Render
    app.run(host="0.0.0.0", port=port, debug=True)