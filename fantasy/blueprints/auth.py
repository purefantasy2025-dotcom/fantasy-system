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

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        account = cursor.fetchone()
        cursor.close()

        if account:
            db_password = account['password']
            password_matches = False

            # Uhakiki wa mseto (Hybrid Check): Kama ni hash au kama ni plain text
            if db_password.startswith(('scrypt:', 'pbkdf2:', 'bcrypt:')):
                password_matches = check_password_hash(db_password, password)
            else:
                # Kama bado ipo kama plain text (mfano '1234')
                password_matches = (db_password == password)

            if password_matches:
                # Kuanzisha Session za mtumiaji
                session['loggedin'] = True
                session['user_id'] = account['id']
                session['username'] = account['username']
                session['role'] = account['role']  # Hapa inabeba 'admin', 'traffic', au 'user'

                flash(f"Welcome back, {account['fullname']}!", 'success')
                
                # Inampeleka moja kwa moja kwenye dashboard
                return redirect(url_for('dashbod.dashboard'))
            else:
                flash('Invalid security password provided!', 'danger')
        else:
            flash('Username identity profile not found!', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role') or 'user'  # Inapokea role yoyote kutoka kwenye fomu
        username = request.form.get('username')
        raw_password = request.form.get('password')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            flash('Identity profile parameters already allocated!', 'warning')
            cursor.close()
        else:
            hashed_password = generate_password_hash(raw_password)
            cursor.execute("""
                INSERT INTO users (fullname, email, phone, role, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (fullname, email, phone, role, username, hashed_password))
            mysql.connection.commit()
            cursor.close()
            
            flash('Registration complete. Proceed with verification.', 'success')
            return redirect(url_for('auth.login'))
            
    return render_template('register.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Session terminated successfully.', 'info')
    return redirect(url_for('public.index'))