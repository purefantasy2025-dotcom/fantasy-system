from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

# --- CONFIGURATION ZA MFUMO ---
app.secret_key = 'siri_yako_ya_usalama_123'

# --- CONFIGURATION ZA MYSQL ---
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '@meddy4BR'
app.config['MYSQL_DB'] = 'school_zone_db'

mysql = MySQL(app)

# --- NJIA (ROUTES) ---

# 1. UKURASA WA NYUMBANI
@app.route('/')
def index():
    return render_template('index.html')

# 2. LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s AND role = %s', 
                       (username, password, role))
        account = cursor.fetchone()

        if account:
            session['loggedin'] = True
            session['username'] = account['username']
            session['role'] = account['role']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials, please try again.")
            
    return render_template('login.html')

# 3. DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        return render_template('dashbod.html', username=session['username'], role=session['role'])
    return redirect(url_for('login'))

# 4. USIMAMIZI WA WATUMIAJI
@app.route('/users')
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users')
        all_users = cursor.fetchall()
        return render_template('user.html', users=all_users)
    return redirect(url_for('login'))

# 5. KUONGEZA MTUMIAJI
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
        cursor.execute('''INSERT INTO users (fullname, email, phone, role, username, password) 
                          VALUES (%s, %s, %s, %s, %s, %s)''', 
                       (fullname, email, phone, role, username, password))
        mysql.connection.commit()
        flash("Mtumiaji mpya ameongezwa!", "success")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

# 6. KUREKEBISHA MTUMIAJI
@app.route('/users/edit/<int:id>', methods=['POST'])
def edit_user(id):
    if 'loggedin' in session:
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        role = request.form.get('role')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''UPDATE users SET fullname=%s, email=%s, phone=%s, role=%s 
                          WHERE id=%s''', (fullname, email, phone, role, id))
        mysql.connection.commit()
        flash("Taarifa zimesasishwa!", "success")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

# 7. KUFUTA MTUMIAJI
@app.route('/users/delete/<int:id>', methods=['POST'])
def delete_user(id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM users WHERE id = %s', (id,))
        mysql.connection.commit()
        flash("Mtumiaji amefutwa!", "warning")
        return redirect(url_for('users'))
    return redirect(url_for('login'))

# 8. VIOLATIONS (Kuvuta data)
@app.route('/violations')
def violations():
    if 'loggedin' in session:
        user_role = session.get('role')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM violations ORDER BY id DESC")
        violations_data = cursor.fetchall() 
        return render_template('violation.html', role=user_role, violations=violations_data)
    return redirect(url_for('login'))

# 9. RESPOND (Kuhifadhi hatua za askari kwenye Database)
@app.route('/respond/<int:id>', methods=['POST'])
def respond(id):
    if 'loggedin' in session:
        # Tunachukua ujumbe kutoka kwenye input ya 'action_message'
        action = request.form.get('action_message')
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # Tunaupdate violation husika kuwa 'Responded' na kuweka ujumbe
        cursor.execute('''UPDATE violations 
                          SET status = 'Responded', response_message = %s 
                          WHERE id = %s''', (action, id))
        mysql.connection.commit()
        
        flash("Hatua imehifadhiwa kikamilifu!", "success")
        return redirect(url_for('violations'))
    return redirect(url_for('login'))

# 10. REPORTS
@app.route('/reports')
def reports():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT COUNT(*) as total_v FROM traffic_logs')
        total_vehicles = cursor.fetchone()['total_v']
        
        cursor.execute('SELECT COUNT(*) as total_viol FROM violations')
        total_violations = cursor.fetchone()['total_viol']
        
        cursor.execute('SELECT HOUR(timestamp) as hr, COUNT(*) as c FROM traffic_logs GROUP BY hr ORDER BY c DESC LIMIT 1')
        peak_data = cursor.fetchone()
        peak_hour = f"{peak_data['hr']}:00" if peak_data else "N/A"

        query = """
            SELECT 
                DATE(timestamp) as date, 
                location_name as location, 
                COUNT(*) as total_vehicles,
                SUM(CASE WHEN speed > 40 THEN 1 ELSE 0 END) as violations
            FROM traffic_logs
            GROUP BY date, location
            ORDER BY date DESC
        """
        cursor.execute(query)
        report_data = cursor.fetchall()
        
        return render_template('report.html', 
                               total_v=total_vehicles, 
                               total_viol=total_violations, 
                               peak=peak_hour,
                               reports=report_data)
    return redirect(url_for('login'))

@app.route('/settings')
def settings():
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)