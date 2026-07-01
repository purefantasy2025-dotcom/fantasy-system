# blueprints/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import mysql

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # 1. Kuanzisha muunganisho wa Database
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # 2. Kuvuta taarifa za mtumiaji kwa usalama
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()
        cursor.close()

        # [DEBUGGING LINE] Hapa ita-print kwenye terminal kuona kama database imepatikana
        print(f"--> Database Response for user '{username}': {account}")

        # 3. Uhakiki wa akaunti na password yenyewe
        if account:
            # Kama data imepatikana, tunahakiki hash ya password
            if check_password_hash(account['password'], password):
                session['loggedin'] = True
                session['user_id'] = account['id']
                session['username'] = account['username']
                session['role'] = account['role']

                flash('Login sequence authenticated.', 'success')
                return redirect(url_for('dashbod.dashboard'))
            else:
                # Password ni mbaya lakini username ipo sahihi
                print("--> Password verification failed!")
                flash('Invalid verification metrics provided! (Wrong Password)', 'danger')
        else:
            # Username haijapatikana kabisa kwenye database
            print("--> Username not found in database!")
            flash('Invalid verification metrics provided! (User Not Found)', 'danger')

    return render_template('login.html')