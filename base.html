from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from datetime import datetime

from app import db

from app.models import Customer
from app.models import Product
from app.models import Payment

payments_bp = Blueprint('payments_bp', __name__)

@payments_bp.route('/payments', methods=['GET', 'POST'])
def payments():

    if request.method == 'POST':

        ref = f"FNT-{datetime.now().strftime('%H%M%S')}"

        payment = Payment(
            ref_number=ref,
            customer_id=request.form['customer_id'],
            product_id=request.form['product_id'],
            amount=request.form['amount'],
            method=request.form['method']
        )

        db.session.add(payment)

        db.session.commit()

        flash("Payment completed")

        return redirect(url_for('payments_bp.payments'))

    payments = Payment.query.all()

    customers = Customer.query.all()

    products = Product.query.all()

    return render_template(
        'payments.html',
        payments=payments,
        customers=customers,
        products=products
    )