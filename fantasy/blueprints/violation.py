from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from extensions import mysql

violation_bp = Blueprint('violation', __name__)

@violation_bp.route('/violations')
def violations():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Access Current Speed Cap Threshold
    cursor.execute("SELECT speed_limit FROM settings WHERE id = 1")
    settings_data = cursor.fetchone()
    speed_limit = settings_data['speed_limit'] if settings_data else 30

    cursor.execute("""
        SELECT *, ROUND(((speed - %s) / %s) * 100, 1) AS exceeded_percent
        FROM violations ORDER BY id DESC
    """, (speed_limit, speed_limit))
    violations_data = cursor.fetchall()
    cursor.close()

    return render_template('violation.html', violations=violations_data, speed_limit=speed_limit, role=session.get('role'))

@violation_bp.route('/violations/single-tap/driver/<int:id>')
def dispatch_driver_notification(id):
    if 'loggedin' not in session or session.get('role') != 'traffic':
        flash('Unauthorized activity vector.', 'danger')
        return redirect(url_for('dashbod.dashboard'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM violations WHERE id = %s", (id,))
    violation = cursor.fetchone()

    if violation:
        msg = f"ALERT: Car {violation['plate_number']} logged traveling {violation['speed']}km/h in a {violation['location_name']}. Fine Issued."
        cursor.execute("""
            INSERT INTO instant_notifications (violation_id, recipient_type, destination, message_body)
            VALUES (%s, 'Driver', 'Driver Cellular Gateway', %s)
        """, (id, msg))
        mysql.connection.commit()
        flash(f"Instant notice dispatched to driver of vehicle {violation['plate_number']}.", 'success')
    
    cursor.close()
    return redirect(url_for('violation.violations'))

@violation_bp.route('/violations/single-tap/admin/<int:id>')
def dispatch_admin_notification(id):
    if 'loggedin' not in session or session.get('role') != 'traffic':
        flash('Unauthorized activity vector.', 'danger')
        return redirect(url_for('dashbod.dashboard'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM violations WHERE id = %s", (id,))
    violation = cursor.fetchone()

    if violation:
        msg = f"CRITICAL CRIME RECORDED: Vehicle {violation['plate_number']} breached speed parameters at {violation['location_name']}."
        
        cursor.execute("""
            INSERT INTO instant_notifications (violation_id, recipient_type, destination, message_body)
            VALUES (%s, 'Administrator', 'Admin Operations Console', %s)
        """, (id, msg))
        
        cursor.execute("""
            UPDATE violations 
            SET status = 'resolved' 
            WHERE id = %s
        """, (id,))
        
        mysql.connection.commit()
        flash('System administrator received the priority telemetry stream data.', 'success')
        
    cursor.close()
    return redirect(url_for('violation.violations'))