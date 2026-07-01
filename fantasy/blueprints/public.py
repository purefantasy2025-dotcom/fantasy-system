# blueprints/public.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
import MySQLdb.cursors
from extensions import mysql

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    query_violations = """
        SELECT 
            id, 
            plate_number, 
            speed, 
            location_name, 
            created_at 
        FROM 
            violations 
        ORDER BY 
            id DESC
    """
    cursor.execute(query_violations)
    violations = cursor.fetchall()
    
    query_comments = """
        SELECT 
            id, 
            violation_id, 
            commenter_name AS name, 
            comment_text, 
            created_at 
        FROM 
            public_comments 
        ORDER BY 
            created_at DESC
    """
    cursor.execute(query_comments)
    comments = cursor.fetchall()
    
    cursor.close()
    
    return render_template(
        'index.html', 
        violations=violations, 
        comments=comments
    )

@public_bp.route('/public/comment/submit', methods=['POST'])
def submit_comment():
    form_data = request.form
    
    violation_id = form_data.get('violation_id')
    raw_name = form_data.get('name')
    comment_text = form_data.get('comment_text')
    
    commenter_name = raw_name if raw_name else 'Anonymous Citizen'
    
    if not comment_text or not violation_id:
        flash('Comment criteria missing.', 'danger')
        return redirect(url_for('public.index'))
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    insert_query = """
        INSERT INTO public_comments (
            violation_id, 
            commenter_name, 
            comment_text
        ) VALUES (
            %s, 
            %s, 
            %s
        )
    """
    
    query_values = (
        violation_id, 
        commenter_name, 
        comment_text
    )
    
    cursor.execute(insert_query, query_values)
    mysql.connection.commit()
    cursor.close()
    
    flash('Public opinion registered successfully!', 'success')
    return redirect(url_for('public.index'))