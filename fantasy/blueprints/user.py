from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from extensions import mysql

user_bp = Blueprint('user', __name__)

@user_bp.route('/users', methods=['GET'])
def users():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('role', 'user').lower() != 'admin':
        flash('Access Denied: Administrative authorization required.', 'danger')
        return redirect(url_for('dashbod.dashboard'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, fullname, email, phone, role FROM users ORDER BY id DESC")
    all_users = cursor.fetchall()
    cursor.close()

    return render_template('user.html', users=all_users, username=session['username'], role=session['role'])


@user_bp.route('/users/add', methods=['POST'])
def add_user():
    if 'loggedin' not in session or session.get('role', 'user').lower() != 'admin':
        return redirect(url_for('auth.login'))

    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    role = request.form.get('role')
    username = request.form.get('username')
    password = request.form.get('password')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (username, email))
    account = cursor.fetchone()

    if account:
        flash('Operation Failed: Username or Email already exists.', 'danger')
    else:
        cursor.execute("""
            INSERT INTO users (fullname, email, phone, role, username, password) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (fullname, email, phone, role, username, password))
        mysql.connection.commit()
        flash('Success: New user profile successfully registered.', 'success')
    
    cursor.close()
    return redirect(url_for('user.users'))


@user_bp.route('/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    if 'loggedin' not in session or session.get('role', 'user').lower() != 'admin':
        return redirect(url_for('auth.login'))

    fullname = request.form.get('fullname')
    email = request.form.get('email')
    phone = request.form.get('phone')
    role = request.form.get('role')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE users 
        SET fullname = %s, email = %s, phone = %s, role = %s 
        WHERE id = %s
    """, (fullname, email, phone, role, id))
    mysql.connection.commit()
    cursor.close()

    flash('Success: User profile updated successfully.', 'success')
    return redirect(url_for('user.users'))


@user_bp.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if 'loggedin' not in session or session.get('role', 'user').lower() != 'admin':
        return redirect(url_for('auth.login'))

    if id == session.get('user_id'):
        flash('Operation Refused: You cannot delete your own active account.', 'warning')
        return redirect(url_for('user.users'))

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()

    flash('Success: User profile permanently removed.', 'success')
    return redirect(url_for('user.users'))