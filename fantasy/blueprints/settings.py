from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from extensions import mysql

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))
        
    if session.get('role', 'user').lower() != 'traffic':
        flash('Access Denied: Administrative privileges required.', 'danger')
        return redirect(url_for('dashbod.dashboard'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        speed_limit = request.form.get('speed_limit')
        alert_email = request.form.get('alert_email')
        log_interval = request.form.get('log_interval')

        # Update the system parameters matching the configuration ledger anchor
        cursor.execute("""
            UPDATE system_settings 
            SET speed_limit = %s, alert_email = %s, log_interval = %s 
            WHERE id = 1
        """, (speed_limit, alert_email, log_interval))
        mysql.connection.commit()
        cursor.close()
        
        flash('Success: System configurations updated successfully.', 'success')
        return redirect(url_for('settings.settings'))

    # Retrieve current active setup properties
    cursor.execute("SELECT * FROM system_settings WHERE id = 1")
    settings_data = cursor.fetchone()
    cursor.close()
    
    # Fallback structure if the database row has not been initialized yet
    if not settings_data:
        settings_data = {
            'speed_limit': 30,
            'alert_email': 'traffic-alerts@domain.local',
            'log_interval': 7
        }

    return render_template(
        'settings.html', 
        settings=settings_data, 
        username=session.get('username'), 
        role=session.get('role', 'user')
    )