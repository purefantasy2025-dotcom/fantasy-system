from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

from app import db
from app.models import Product

products_bp = Blueprint('products_bp', __name__)

@products_bp.route('/products', methods=['GET', 'POST'])
def products():

    if request.method == 'POST':

        product = Product(
            product_name=request.form['product_name'],
            product_code=request.form['product_code'],
            price=request.form['price'],
            stock=request.form['stock']
        )

        db.session.add(product)

        db.session.commit()

        flash("Product added")

        return redirect(url_for('products_bp.products'))

    products = Product.query.all()

    return render_template(
        'products.html',
        products=products
    )