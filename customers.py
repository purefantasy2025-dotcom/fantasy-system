from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app import db
from app.models import Customer

customers_bp = Blueprint('customers_bp', __name__)

@customers_bp.route('/customers', methods=['GET', 'POST'])
def customers():

    if request.method == 'POST':

        try:

            customer = Customer(
                name=request.form['name'],
                phone=request.form['phone'],
                email=request.form['email']
            )

            db.session.add(customer)

            db.session.commit()

            flash("Customer added successfully")

        except:

            flash("Phone number already exists")

        return redirect(url_for('customers_bp.customers'))

    customers = Customer.query.all()

    return render_template(
        'customers.html',
        customers=customers
    )