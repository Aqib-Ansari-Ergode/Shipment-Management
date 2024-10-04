from flask import Flask, render_template, request, redirect, send_file, url_for, session,jsonify
from datetime import datetime
import SQL_functions as sqlf
import pandas as pd
import os
import csv
import json

app = Flask(__name__)

app.secret_key = 'your_secret_key'

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

@app.route('/')
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

@app.route('/get_delivered', methods=['POST'])
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

@app.route('/get_delivered_details')
def get_delivered_details():
    sanitize_session_values()
    
    # Fetch data from the SQL function based on session filters
    if session['post_done']:
        table_data = sqlf.get_delivered(start=session['start_date'], end=session['end_date'],
                                        venue=session['venue'], carrier=session['carrier'], columns=True)
    else:
        table_data = sqlf.get_delivered(start=None, end=None, venue=None, carrier=None, columns=True)
    
    # Save the total number of records for pagination
    session["len_delivered_data"] = len(table_data)

    # Convert table_data to DataFrame
    data = [list(row) for row in table_data]
    df = pd.DataFrame(data, columns=['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                                     'Purchase Date', 'Current Status', 'Status Update Date', 'Scheduled Delivery Date'])
    
    # Handle the CSV file creation logic
    file_name = f"{session['start_date'] or 'begin-to'}_{session['end_date'] or 'today'}_{session['venue'] or 'all-venues'}_{session['carrier'] or 'all-carriers'}.csv"
    session['file_name'] = file_name
    df.to_csv(f"files/{file_name}", index=False)

    # Pagination logic
    records_per_page = 25
    total_pages = (session['len_delivered_data'] + records_per_page - 1) // records_per_page  # Ceiling division for total pages
    current_page = int(session.get('page_no', 1))
    print(current_page)  # Default to page 1 if not set
    
    if total_pages>10:
        total_pages_s =10
    else:
        total_pages_s = total_pages
    # Slice the data for the current page
    start_index = (current_page - 1) * records_per_page
    end_index = start_index + records_per_page
    table_data_paginated = table_data[start_index:end_index]
    print(start_index)
    print(end_index)
    print(table_data_paginated)

    # Render the paginated data in the template
    return render_template('Delivered.html', 
                           table_data=table_data_paginated, 
                           file_name=file_name, 
                           total_pages_s=total_pages_s, 
                           current_page=current_page)

FILE_DIRECTORY = './files/'

@app.route('/download')
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

@app.route('/add_tag', methods=['POST'])
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

import json

@app.route('/add_tag_manual', methods=['GET', 'POST'])
def add_tag_manual():
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()

    # Load the JSON file containing shipment status data
    with open('shipments.json') as json_file:
        shipment_data = json.load(json_file)

    if request.method == 'POST':
        # You can process the data coming from the form here
        start_date_sel = request.form.get('start_date')
        end_date_sel = request.form.get('end_date')
        status_sel = request.form.get('status')
        tag_sel = request.form.getlist('tag')
        venue_sel = request.form.get('venue')
        carrier_sel = request.form.get('carrier')
        
        print(f"Start Date: {start_date_sel}")
        print(f"End Date: {end_date_sel}")
        print(f"Dropdown 1: {status_sel}")
        print(f"Dropdown 2: {tag_sel}")
        print(f"Dropdown 3: {venue_sel}")
        print(f"Dropdown 4: {carrier_sel}")
        venue_sele = venue_sel
        carrier_sele = carrier_sel
        if venue_sel == 'Venues':
            venue_sele = False
        if carrier_sel == 'Carriers':
            carrier_sele = False
        # Implement logic to handle the tag (like adding it to the database)
        data = sqlf.get_delivered(start=start_date_sel,
                                  end=end_date_sel,
                                  venue=venue_sele,
                                  carrier=carrier_sele, columns=True)

        columns = ['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                   'Purchase Date', 'Current Status', 'Status Update Date', 'Scheduled Delivery Date']
        table_data_paginated = data[25 * (int(session['page_no']) - 1):25 * int(session['page_no'])]

        return render_template('tag_management.html',
                               data=table_data_paginated, venues=venues,
                               columns=columns, carriers=carriers, venue_sel=venue_sel,
                               carrier_sel=carrier_sel, start_date_sel=start_date_sel,
                               status_sel=status_sel, end_date_sel=end_date_sel, tag_sel=tag_sel,
                               shipment_data=shipment_data)

    return render_template('tag_management.html', venues=venues, carriers=carriers,shipment_data=shipment_data)


def load_data():
    try:
        with open('shipments.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Save data to a JSON file
def save_data(data):
    with open('shipments.json', 'w') as file:
        json.dump(data, file, indent=4)

@app.route('/update_tag', methods=['POST'])
def update_tag():
    # Load the existing data
    data = load_data()

    # Get the form data (assuming each key is something like 'status_<shipment_number>')
    form_data = request.form

    # Iterate over form data and update the data dict based on shipment numbers
    for key, value in form_data.items():
          # Assume fields with 'status_' prefix
            # Extract shipment number from the form field name
            shipment_number = key
            # Update the data with the new status
            data[shipment_number] = value

    # Save the updated data back to the JSON file
    save_data(data)

    return jsonify({"message": "Data successfully updated."})

@app.route('/next_page', methods=['GET'])
def next_page():
    # Get the total number of pages (assuming you have table_data length available)
    total_records = session["len_delivered_data"]  # Adjust based on your actual data retrieval logic
    records_per_page = 25
    total_pages = (total_records + records_per_page - 1) // records_per_page  # Ceiling division

    # Increment the page number, but ensure it doesn't exceed the total number of pages
    if 'page_no' in session:
        session['page_no'] = min(int(session['page_no']) + 1, total_pages)
    else:
        session['page_no'] = 1

    return redirect(url_for('get_delivered_details'))

@app.route('/prev_page', methods=['GET'])
def prev_page():
    # Decrement the page number in the session but ensure it doesn't go below 1
    if 'page_no' in session and session['page_no'] > 1:
        session['page_no'] = int(session['page_no']) - 1
    else:
        session['page_no'] = 1

    # Redirect to the route that displays the delivered details
    return redirect(url_for('get_delivered_details'))


if __name__ == '__main__':
    app.run(debug=True, port=8080)
