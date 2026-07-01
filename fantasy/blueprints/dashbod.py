# blueprints/dashbod.py
from flask import Blueprint, render_template, session, redirect, url_for
import MySQLdb.cursors
import MySQLdb
from extensions import mysql

dashbod_bp = Blueprint('dashbod', __name__)

@dashbod_bp.route('/dashboard')
def dashboard():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    user_role = session.get('role', 'user')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Metric 1: Count vehicles registered today
    cursor.execute("SELECT COUNT(*) AS today_count FROM traffic_logs WHERE DATE(timestamp) = CURRENT_DATE")
    daily_vehicle_count = cursor.fetchone()['today_count']
    
    # Metric 2: Count outstanding citations
    cursor.execute("SELECT COUNT(*) AS active_violations FROM violations WHERE status='Pending'")
    active_violations = cursor.fetchone()['active_violations']
    
    # Inatafuta jumla ya ujumbe uliopo kwa sasa kwa ajili ya kuhesabiwa na JavaScript
    total_messages = 0
    try:
        cursor.execute("SELECT COUNT(*) AS msg_count FROM system_messages WHERE recipient_role = %s", (user_role,))
        total_messages = cursor.fetchone()['msg_count']
    except (MySQLdb.ProgrammingError, MySQLdb.OperationalError):
        total_messages = 0
    
    cursor.close()

    return render_template(
        'dashbod.html',
        username=session['username'],
        role=user_role,
        daily_vehicle_count=daily_vehicle_count,
        active_violations=active_violations,
        total_messages=total_messages
    )