# blueprints/invoice_details.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
import MySQLdb.cursors
from datetime import datetime
import random
from extensions import mysql

invoice_bp = Blueprint('invoice_details', __name__)

@invoice_bp.route('/invoice/generate/<int:id>')
def generate_invoice(id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM violations WHERE id=%s", (id,))
    violation = cursor.fetchone()

    if not violation:
        cursor.close()
        flash('Violation reference not matching active records.', 'danger')
        return redirect(url_for('violation.violations'))

    cursor.execute("SELECT * FROM invoices WHERE violation_id=%s", (id,))
    if cursor.fetchone():
        cursor.close()
        return redirect(url_for('invoice_details.invoice_details', id=id))

    ctrl_num = "TZ" + str(random.randint(100000000, 999999999))
    inv_num = "INV" + str(random.randint(100000, 999999))
    
    cursor.execute("""
        INSERT INTO invoices (violation_id, invoice_number, plate_number, control_number, amount, payment_status)
        VALUES (%s, %s, %s, %s, 50000.00, 'UNPAID')
    """, (violation['id'], inv_num, violation['plate_number'], ctrl_num))
    
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('invoice_details.invoice_details', id=id))

@invoice_bp.route('/invoice/details/<int:id>')
def invoice_details(id):
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM invoices WHERE violation_id=%s", (id,))
    invoice = cursor.fetchone()
    cursor.close()

    if not invoice:
        flash('Target citation ledger missing invoice references.', 'warning')
        return redirect(url_for('violation.violations'))

    # Calculate 40% school benefit share on the Python backend dynamically
    # This prevents the Jinja2 'Undefined.__format__' TypeError in the HTML template
    invoice['school_share'] = float(invoice['amount']) * 0.40

    return render_template('invoice_details.html', invoice=invoice)