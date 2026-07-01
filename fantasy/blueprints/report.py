# blueprints/report.py
from flask import Blueprint, render_template, redirect, url_for, session
import MySQLdb.cursors
from extensions import mysql

report_bp = Blueprint('report', __name__)

@report_bp.route('/report/dashboard')
def reports():
    if 'loggedin' not in session:
        return redirect(url_for('auth.login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # 1. AUTOMATIC WEEKLY SUMMARY (Salama dhidi ya thamani za NULL/None)
    # Tunatumia COALESCE ya SQL kuhakikisha kama hakuna data, inarudisha 0 badala ya NULL
    cursor.execute("""
        SELECT 
            COUNT(*) AS total_citations,
            COALESCE(SUM(amount), 0.0) AS total_revenue,
            COALESCE(SUM(amount) * 0.40, 0.0) AS school_share_total
        FROM invoices
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
    """)
    weekly_summary = cursor.fetchone()

    # Double check kwa upande wa Python kuhakikisha hakuna variable inayokwenda ikiwa 'None'
    total_citations = weekly_summary['total_citations'] if weekly_summary['total_citations'] is not None else 0
    total_revenue = weekly_summary['total_revenue'] if weekly_summary['total_revenue'] is not None else 0.0
    school_share_total = weekly_summary['school_share_total'] if weekly_summary['school_share_total'] is not None else 0.0

    # 2. AUTOMATIC WEEKLY INVOICES LEDGER
    cursor.execute("""
        SELECT invoice_number, plate_number, control_number, amount, payment_status, created_at
        FROM invoices
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        ORDER BY created_at DESC
    """)
    weekly_invoices = cursor.fetchall()
    
    cursor.close()

    return render_template(
        'report.html',
        username=session['username'],
        role=session.get('role', 'user'),
        total_citations=total_citations,
        total_revenue=float(total_revenue),
        school_share_total=float(school_share_total),
        invoices=weekly_invoices
    )