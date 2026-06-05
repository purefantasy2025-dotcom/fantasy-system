from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import time
import os

app = Flask(__name__)

# SYSTEM CONFIGURATION
app.secret_key = 'my_secret_key_123'

#  MYSQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@meddy4BR'
app.config['MYSQL_DB'] = 'school_zone_db'
mysql = MySQL(app)

# HOME PAGE
@app.route('/')
def index():
    return render_template('index.html')

# LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM users WHERE username = %s AND password = %s AND role = %s',
            (username, password, role)
        )
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = account['role']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.")
    return render_template('login.html')

# REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        # CHECK IF USER EXISTS
        cursor.execute(
            'SELECT * FROM users WHERE username = %s OR email = %s',
            (username, email)
        )
        account = cursor.fetchone()
        if account:
            flash('Account already exists!')
        else:
            cursor.execute('''
                INSERT INTO users (fullname, email, phone, role, username, password)
                VALUES (%s, %s, %s, %s, %s, %s)
            ''', (fullname, email, phone, role, username, password))
            mysql.connection.commit()
            flash('Registration successful!')
            return redirect(url_for('login'))
    return render_template('register.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template(
            'dashbod.html',
            username=session['username'],
            role=session['role']
        )
    return redirect(url_for('login'))

# USERS LIST
@app.route('/users')
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users')
        all_users = cursor.fetchall()
        return render_template('user.html', users=all_users)
    return redirect(url_for('login'))

    # ADD USER
@app.route('/users/add', methods=['POST'])
def add_user():
    if 'loggedin' in session:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        username = request.form.get('username')
        password = request.form.get('password')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            INSERT INTO users (fullname, email, phone, role, username, password)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (fullname, email, phone, role, username, password))
        mysql.connection.commit()
        flash("Mtumiaji mpya ameongezwa!", "success")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

    # EDIT USER
@app.route('/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    if 'loggedin' in session:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            UPDATE users 
            SET fullname=%s, email=%s, phone=%s, role=%s 
            WHERE id=%s
        ''', (fullname, email, phone, role, id))
        mysql.connection.commit()
        flash("Taarifa zimesasishwa!", "success")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

    # DELETE USER
@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))
        mysql.connection.commit()
        flash("User deleted!", "warning")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

# VIOLATIONS + ALERTS
# =========================
# VIOLATIONS ROUTE
# =========================
@app.route('/violations')
def violations():
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    role = session.get('role')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # GET SPEED LIMIT FROM SETTINGS (DYNAMIC)
    cursor.execute("SELECT speed_limit FROM settings WHERE id=1")
    settings = cursor.fetchone()
    speed_limit = settings['speed_limit'] if settings and 'speed_limit' in settings else 40

    # GET VIOLATIONS WITH CALCULATION
    cursor.execute("""
        SELECT *,
        ROUND(((speed - %s) / %s) * 100, 1) AS exceeded_percent
        FROM violations
        ORDER BY id DESC
    """, (speed_limit, speed_limit))

    violations_data = cursor.fetchall()

    # GET ALERTS
    cursor.execute("""
        SELECT * FROM alerts
        ORDER BY alert_id DESC
    """)
    alerts_data = cursor.fetchall()

    cursor.close()

    return render_template(
        'violation.html',
        violations=violations_data,
        alerts=alerts_data,
        role=role,
        speed_limit=speed_limit
    )

# RESPOND TO VIOLATION
@app.route('/respond/<int:id>', methods=['POST'])
def respond(id):
    if 'loggedin' not in session:
        return redirect(url_for('login'))

    action = request.form.get('action_message')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("""
        UPDATE violations 
        SET status = 'Responded',
            response_message = %s 
        WHERE id = %s
    """, (action, id))

    mysql.connection.commit()
    cursor.close()

    flash("Response recorded successfully!", "success")

    return redirect(url_for('violations'))

# REPORTS
@app.route('/reports')
def reports():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) as total_v FROM traffic_logs')
        total_vehicles = cursor.fetchone()['total_v']
        cursor.execute('SELECT COUNT(*) as total_viol FROM violations')
        total_violations = cursor.fetchone()['total_viol']
        cursor.execute('''
            SELECT HOUR(timestamp) as hr, COUNT(*) as c 
            FROM traffic_logs 
            GROUP BY hr 
            ORDER BY c DESC 
            LIMIT 1
        ''')
        peak_data = cursor.fetchone()
        peak_hour = f"{peak_data['hr']}:00" if peak_data else "N/A"
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date, 
                location_name as location, 
                COUNT(*) as total_vehicles,
                SUM(CASE WHEN speed > 40 THEN 1 ELSE 0 END) as violations
            FROM traffic_logs
            GROUP BY date, location
            ORDER BY date DESC
        """)
        report_data = cursor.fetchall()

        return render_template(
            'report.html',
            total_v=total_vehicles,
            total_viol=total_violations,
            peak=peak_hour,
            reports=report_data
        )
    return redirect(url_for('login'))

# SETTINGS
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == 'POST':
        speed = request.form.get('speed')
        location = request.form.get('location')
        if speed and location:
            cursor.execute("""
                UPDATE settings
                SET speed_limit=%s,
                    location_name=%s
                WHERE id=1
            """, (speed, location))
            mysql.connection.commit()
            flash("Settings Updated Successfully!")
    cursor.execute("SELECT * FROM settings WHERE id=1")
    settings_data = cursor.fetchone()
    return render_template('settings.html', settings=settings_data)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# RUN APP

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
