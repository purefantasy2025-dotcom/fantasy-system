from flask import Blueprint
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import flash

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == '1234':

            return redirect(url_for('dashboard_bp.dashboard'))

        flash("Username au Password si sahihi")

    return render_template('login.html')