from flask import Flask, render_template, request, redirect, send_file, url_for, session
from datetime import datetime
import SQL_functions as sqlf
import pandas as pd
import os
import csv

application = Flask(__name__)

application.secret_key = 'your_secret_key'

def clear_session():
    session.clear()
    session['post_done'] = False
    session['start_date'] = False
    session['end_date'] = False
    session['venue'] = False
    session['carrier'] = False
    session['page_no'] = 1

def sanitize_session_values():
    # Ensures all session values are properly set
    if not session.get('start_date'):
        session['start_date'] = False
    if not session.get('end_date'):
        session['end_date'] = False
    if not session.get('venue'):
        session['venue'] = False
    if not session.get('carrier'):
        session['carrier'] = False
    if not session.get('page_no'):
        session['page_no'] = 1

@application.route('/')
def index():
    clear_session()
    current_date = datetime.now().strftime("%Y-%m-%d")
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()

    aux_hold_cases = [{'delivered': list(sqlf.get_delivered()[0])[0]}]
    warehouse_cases = [
        {'quantity': 50, 'status': 'Ready to Ship'},
        {'quantity': 100, 'status': 'Ready to Ship'},
        {'quantity': 60, 'status': 'Packing'},
        {'quantity': 20, 'status': 'Packing'},
        {'quantity': 80, 'status': 'Ready to Ship'}
    ]

    return render_template('index.html', current_date=current_date, aux_hold_cases=aux_hold_cases,
                           warehouse_cases=warehouse_cases, venues=venues, carriers=carriers)

@application.route('/get_delivered', methods=['POST'])
def handle_get_delivered():
    current_date = datetime.now().strftime("%Y-%m-%d")
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()

    if request.method == 'POST':
    # Get form data or set False if the field is empty or None
        session['start_date'] = request.form.get('start_date') or False
        session['end_date'] = request.form.get('end_date') or False
        session['venue'] = request.form.get('venue') or False
        session['carrier'] = request.form.get('carrier') or False
        session['post_done'] = True
        session['page_no'] = 1
        print(session['start_date'])
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        print("--"*20)
        sanitize_session_values()
        print(session['start_date']==False)
        print(session['end_date']==False)
        print(session['venue']==False)
        print(session['carrier']==False)
        if session['venue'] == 'Filter by Venue':
            session['venue'] = False
        if session['carrier'] == 'Filter by Carrier':
            session['carrier'] = False
         # Handle aux_hold_cases as per the retrieved values
        aux_hold_cases = [{'delivered': list(sqlf.get_delivered(start=session['start_date'],
                                                            end=session['end_date'],
                                                            venue=session['venue'],
                                                            carrier=session['carrier']))[0][0]}]


        warehouse_cases = [
            {'quantity': 50, 'status': 'Ready to Ship'},
            {'quantity': 100, 'status': 'Ready to Ship'},
            {'quantity': 60, 'status': 'Packing'},
            {'quantity': 20, 'status': 'Packing'},
            {'quantity': 80, 'status': 'Ready to Ship'}
        ]
        return render_template('index.html', current_date=current_date, aux_hold_cases=aux_hold_cases,
                               warehouse_cases=warehouse_cases, venues=venues,
                               start_date=session['start_date'], end_date=session['end_date'],
                               venue_sel=session['venue'], carriers=carriers, carrier_sel=session['carrier'])

@application.route('/get_delivered_details')
def get_delivered_details():
    sanitize_session_values()
    if session['post_done']:
        table_data = sqlf.get_delivered(start=session['start_date'], end=session['end_date'],
                                        venue=session['venue'], carrier=session['carrier'], columns=True)
    else:
        table_data = sqlf.get_delivered(start=None, end=None, venue=None, carrier=None, columns=True)

    data = [list(row) for row in table_data]
    df = pd.DataFrame(data, columns=['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                                     'Purchase Date', 'Current Status', 'Status Update Date', 'Scheduled Delivery Date'])
    
    if session['venue'] == 'False':
        session['venue'] = False
    if session['carrier'] == 'False':
        session['carrier'] = False

    file_name = f"{session['start_date'] or 'begin-to'}_{session['end_date'] or "today"}_{session['venue'] or "all-venues"}_{session['carrier'] or "all-carriers"}.csv"
    session['file_name'] = file_name
    df.to_csv(f"files/{file_name}", index=False)

    table_data_paginated = table_data[25 * (int(session['page_no']) - 1):25 * int(session['page_no'])]
    return render_template('Delivered.html', table_data=table_data_paginated, file_name=file_name)

FILE_DIRECTORY = './files/'

@application.route('/download')
def download_file():
    try:
        # Ensure session has file_name
        if 'file_name' not in session or not session['file_name']:
            return "No file available for download", 400

        file_path = os.path.join(FILE_DIRECTORY, session['file_name'])
        
        # Check if the file exists
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return f"File '{session['file_name']}' not found", 404

    except Exception as e:
        return f"Error occurred: {str(e)}", 500

@application.route('/add_tag', methods=['POST'])
def add_tag():
    csv_file = 'tags_with_order_ids.csv'

    try:
        with open(csv_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(['Shipment_number', 'Tag'])

            for tag in request.form.items():
                writer.writerow([tag[0], tag[1]])

        return redirect(url_for('get_delivered_details'))
    except Exception as e:
        return f"Error occurred while adding tag: {str(e)}"

if __name__ == '__main__':
    application.run(host='0.0.0.0', port=8080)
