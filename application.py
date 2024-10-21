from flask import Flask, render_template, request, redirect, send_file, url_for, session, jsonify, flash, g
from datetime import datetime
import SQL_functions as sqlf
import pandas as pd
import os
import csv
import json
import openpyxl
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'your_secret_key'
users = {
    "testuser@gmail.com": "Apassword123A"  # Username: Password
}
from functools import wraps

def setup_logging():
    handler = RotatingFileHandler(
        "logs/app.log", maxBytes=100000, backupCount=3
    )
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s - [in %(pathname)s:%(lineno)d]"
    )
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

setup_logging()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def delete_all_files(folder_path):
    try:
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    app.logger.info(f"Deleted: {file_path}")
        else:
            app.logger.warning("The specified folder does not exist or is not a directory.")
    except Exception as e:
        app.logger.error(f"Error deleting files: {str(e)}")

def clear_session():
    app.logger.warning(f"Clearing session username from {request.remote_addr}")
    session.clear()
    session.update({'post_done': False, 'start_date': False, 'end_date': False, 'venue': False, 
                    'carrier': False, 'page_no': 1})

def sanitize_session_values():
    session.setdefault('start_date', False)
    session.setdefault('end_date', False)
    session.setdefault('venue', False)
    session.setdefault('carrier', False)
    session.setdefault('page_no', 1)

@app.route('/')
@login_required
def index():
    try:
        delete_all_files('files')
        delete_all_files('tags_files')
        clear_session()
        session["user"] = 'Admin'
        app.logger.info(f"User '{session['user']}' accessed the dashboard.")

        session['current_date'] = datetime.now().strftime("%Y-%m-%d")
        aux_hold_cases = [{'delivered': sql_query_handler(sqlf.get_delivered)}]
        
        warehouse_cases = [{'quantity': 50, 'status': 'Ready to Ship'}, ...]

        return render_template('index.html', aux_hold_cases=aux_hold_cases,
                               warehouse_cases=warehouse_cases, venues=get_venues(), carriers=get_carriers())
    except Exception as e:
        app.logger.error(f"Error in index route: {str(e)}")
        return "An error occurred", 500

def sql_query_handler(sql_func, *args, **kwargs):
    try:
        result = sql_func(*args, **kwargs)
        app.logger.info(f"SQL query executed successfully: {sql_func.__name__}")
        return result
    except Exception as e:
        app.logger.error(f"SQL query failed: {sql_func.__name__} - {str(e)}")
        return []

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['email']
        password = request.form['password']

        if users.get(username) == password:
            session['username'] = username
            flash('Login successful!', 'success')
            app.logger.info(f"User '{username}' logged in successfully.")
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
            app.logger.warning(f"Failed login attempt for username: {username}")

    return render_template('login.html')

@app.route('/get_delivered', methods=['POST'])
@login_required
def handle_get_delivered():
    try:
        sanitize_session_values()
        session.update({
            'start_date': request.form.get('start_date') or False,
            'end_date': request.form.get('end_date') or False,
            'venue': request.form.get('venue') or False,
            'carrier': request.form.get('carrier') or False,
            'post_done': True, 'page_no': 1
        })

        aux_hold_cases = [{'delivered': sql_query_handler(sqlf.get_delivered,
                              start=session['start_date'], end=session['end_date'],
                              venue=session['venue'], carrier=session['carrier'])}]

        return render_template('index.html', aux_hold_cases=aux_hold_cases,
                               venues=get_venues(), carriers=get_carriers())
    except Exception as e:
        app.logger.error(f"Error in handle_get_delivered: {str(e)}")
        return "An error occurred", 500

def get_venues():
    return sql_query_handler(sqlf.get_venues)

def get_carriers():
    return sql_query_handler(sqlf.get_carriers)
FILE_DIRECTORY = './files/'
@app.route('/download')
@login_required
def download_file():
    try:
        file_path = os.path.join(FILE_DIRECTORY, session.get('file_name', ''))
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            app.logger.warning(f"File '{file_path}' not found.")
            return f"File '{session.get('file_name')}' not found", 404
    except Exception as e:
        app.logger.error(f"Error downloading file: {str(e)}")
        return "An error occurred", 500



@app.route('/add_tag_manual', methods=['POST'])
def add_tag_manual():
    # Get tags from the form submission (tags is a dictionary with order_id as keys)
    # form_data = request.form.items()
    # print(form_data)
    # for i in form_data:
    #     print(i)
    # Define the file path for the CSV (you can choose your own path)
    csv_file = 'tags_with_order_ids.csv'

    # Open the CSV file in append mode, and write each tag with its corresponding order_id
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        # Write header if file is new (only needed the first time)
        file.seek(0, 2)  # Move the pointer to the end to check file size
        if file.tell() == 0:
            writer.writerow(['Shipment_number','Tag'])  # Write the header once if the file is new

        # Loop through the form data and write each order_id and tag to the CSV file
        for tag in request.form.items():
            writer.writerow([tag[0],tag[1]])
    return redirect(url_for('get_delivered_details'))

    # After saving, redirect to another route or page
    
def clear_session():
    session.clear()

if __name__ == '__main__':
    app.run(debug=True,port=8080)
    session.clear()
    
