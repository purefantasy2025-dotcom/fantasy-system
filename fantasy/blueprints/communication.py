# blueprints/communication.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import MySQLdb.cursors
from extensions import mysql

comms_bp = Blueprint('communication', __name__)

@comms_bp.route('/communication/portal', methods=['GET', 'POST'])
def portal():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == 'POST':
        recipient_role = request.form.get('recipient_role')
        subject = request.form.get('subject')
        message_text = request.form.get('message_text')
        
        cursor.execute("""
            INSERT INTO system_messages (sender_id, recipient_role, subject, message_text)
            VALUES (%s, %s, %s, %s)
        """, (session['user_id'], recipient_role, subject, message_text))
        mysql.connection.commit()
        flash('Communication thread transmitted across secure pipeline.', 'success')
        return redirect(url_for('communication.portal'))
        
    # Inapakia ujumbe kulingana na jukumu (role) la mtumiaji aliyelogin
    cursor.execute("""
        SELECT m.*, u.username as sender_name, u.role as sender_role 
        FROM system_messages m 
        JOIN users u ON m.sender_id = u.id 
        WHERE m.recipient_role = %s 
        ORDER BY m.timestamp DESC
    """, (session['role'],))
    received_messages = cursor.fetchall()
    cursor.close()
    
    return render_template('communication.html', messages=received_messages, role=session['role'])