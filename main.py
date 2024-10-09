from flask import Flask, render_template, request, redirect, send_file, url_for, session,jsonify,flash
from datetime import datetime
import SQL_functions as sqlf
import pandas as pd
import os
import csv
import json

app = Flask(__name__)

app.secret_key = 'your_secret_key'

def delete_all_files(folder_path):
    # Check if the folder exists
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        # Iterate over all files in the folder
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            # Check if it's a file
            if os.path.isfile(file_path):
                os.remove(file_path)  # Delete the file
                print(f"Deleted: {file_path}")
    else:
        print("The specified folder does not exist or is not a directory.")


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
    delete_all_files('files')
    delete_all_files('tags_files')
    clear_session()
    session["user"] = 'Admin'
    current_date = datetime.now().strftime("%Y-%m-%d")
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()
    session['current_date'] = current_date

    aux_hold_cases = [{'delivered': list(sqlf.get_delivered()[0])[0]}]
    warehouse_cases = [
        {'quantity': 50, 'status': 'Ready to Ship'},
        {'quantity': 100, 'status': 'Ready to Ship'},
        {'quantity': 60, 'status': 'Packing'},
        {'quantity': 20, 'status': 'Packing'},
        {'quantity': 80, 'status': 'Ready to Ship'}
    ]

    return render_template('index.html', current_date=session['current_date'], aux_hold_cases=aux_hold_cases,
                           warehouse_cases=warehouse_cases, venues=venues, carriers=carriers)

users = {
    "testuser": "password123"  # Username: Password
}

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        remember = request.form.get('remember')

        # Validate username and password
        if username in users and users[username] == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))  # Redirect to dashboard or another page
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

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

    # Get the page number from the query parameters
    current_page = int(request.args.get('page_no', 1))  # Default to page 1 if not provided

    # Fetch data from the SQL function based on session filters
    if session.get('post_done', False):
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

    if total_pages > 10:
        total_pages_s = 10
    else:
        total_pages_s = total_pages

    # Ensure the current page is within the valid range
    current_page = max(1, min(current_page, total_pages))

    # Slice the data for the current page
    start_index = (current_page - 1) * records_per_page
    end_index = start_index + records_per_page
    table_data_paginated = table_data[start_index:end_index]

    # Render the paginated data in the template
    return render_template('Delivered.html',
                           table_data=table_data_paginated,
                           file_name=file_name,
                           total_pages_s=total_pages_s,
                           current_page=current_page,
                           total_pages=total_pages)

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


@app.route('/add_tag_manual', methods=['GET', 'POST'])
def add_tag_manual():
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()
    log_file_path = 'log_dates.json'

    # Load existing logs if available
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            try:
                log_dates = json.load(log_file)
                
            except json.JSONDecodeError:
                log_dates = {}
    else:
        log_dates = {}

    # Load the JSON file containing shipment status data
    shipment_data = {}
    for i in log_dates:
        shipment_data[i] = log_dates[i]["current_status"]
        
    
    current_page = int(request.args.get('page', 1))
    records_per_page = 25
    if request.method == 'POST':
        # You can process the data coming from the form here
        session['start_date_sel'] = request.form.get('start_date')
        session['end_date_sel'] = request.form.get('end_date')
        session['status_sel'] = request.form.get('status')
        session['tag_sel'] = request.form.getlist('tag')
        session['venue_sel'] = request.form.get('venue')
        session['carrier_sel'] = request.form.get('carrier')
        session['shipment_number'] = request.form.get('shipment_number')
        
        print(f"Start Date: {session['start_date_sel']}")
        print(f"End Date: {session['end_date_sel']}")
        print(f"Dropdown 1: {session['status_sel']}")
        print(f"Dropdown 2: {session['tag_sel']}")
        print(f"Dropdown 3: {session['venue_sel']}")
        print(f"Dropdown 4: {session['carrier_sel']}")
        print(f"Shipment Number : {session['shipment_number']}")
        

        venue_sele = session["venue_sel"]
        carrier_sele = session['carrier_sel'] 
        if session['venue_sel'] == 'Venues':
            venue_sele = False
        if session['carrier_sel'] == 'Carriers':
            carrier_sele = False
        if session['status_sel'] == 'Status':
            session['status_sel'] = False
        # Implement logic to handle the tag (like adding it to the database)
        shipment_numbers = [key for key, value in shipment_data.items() if value in session['tag_sel']]
        print(shipment_numbers)
        if 'shipment_number' in session:
            if session["shipment_number"] == False or session['shipment_number'] == "":
                data = sqlf.get_data(start=session['start_date_sel'],
                                  end=session['end_date_sel'],
                                  venue=venue_sele,
                                  carrier=carrier_sele,shipment_numbers=shipment_numbers,status=session['status_sel'])
                # for i in data[0]:
                    # print(i)
                print(data[0][7])
            else:
                data = sqlf.get_data(start=False,
                                  end=False,
                                  venue=False,
                                  carrier=False,shipment_numbers=False,shipment_number = session['shipment_number'])
        columns = ['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                   'Purchase Date','status','Our Status' ,'Current Status', 'Status Update Date', 'Scheduled Delivery Date']
        total_records = len(data)
        total_pages = (total_records + records_per_page - 1) // records_per_page  # Ceiling division
        table_data_paginated = data[(current_page - 1) * records_per_page: current_page * records_per_page]
        df_data = [list(row) for row in data]
        df_data = pd.DataFrame(data, columns = ['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                   'Purchase Date','status' ,'Current Status', 'Status Update Date', 'Scheduled Delivery Date'])
        

        shipment_df = pd.DataFrame(list(shipment_data.items()), columns=['Shipment Number', 'Tag'])
        df_data = df_data.merge(shipment_df, on='Shipment Number', how='left')
        file_name = f"{session['start_date_sel'] or 'begin-to'}_{session['end_date_sel'] or session['current_date']}_{venue_sele or 'all-venues'}_{carrier_sele or 'all-carriers'}_{session['status_sel'] or "all-status"}_{session['tag_sel'] or 'all-tags'}.csv"
        session['file_name_tagged'] = file_name
        df_data.to_csv(f"tags_files/{file_name}", index=False)

        return render_template('tag_management.html',
                               data=table_data_paginated, venues=venues,
                               columns=columns, carriers=carriers, venue_sel=session['venue_sel'],
                               carrier_sel=session['carrier_sel'], start_date_sel=session['start_date_sel'],
                               status_sel=session['status_sel'], end_date_sel=session['end_date_sel'], tag_sel=session['tag_sel'],
                               shipment_data=shipment_data,current_page=current_page,total_pages=total_pages , downl = True,log_dates=log_dates)
    print('venue_sel' in session)
    print('start_date_sel' in session)
    print('end_date_sel' in session)
    print('carrier_sel' in session)
    # print('venue_sel' in session)
    if 'venue_sel' in session and 'start_date_sel' in session and 'end_date_sel' in session and "carrier_sel" in session:
       
            
            if session['venue_sel'] == 'Venues':
                session['venue_sel'] = False
            if session['carrier_sel'] == 'Carriers':
                session['carrier_sel'] = False
            if session['start_date_sel'] == '':
                session['start_date_sel'] = False
            if session['end_date_sel'] == '':
                session['end_date_sel'] = False
            # print(session['venue_sel'])
            print(session['venue_sel'])
            print(session['start_date_sel'])
            print(session['end_date_sel'])
            print(session['carrier_sel'])
            shipment_numbers = [key for key, value in shipment_data.items() if value in session['tag_sel']]
            print(shipment_numbers)
            data = sqlf.get_data(start=session['start_date_sel'],
                                        end=session['end_date_sel'],
                                        venue=session['venue_sel'],
                                        carrier=session['carrier_sel'],shipment_numbers=shipment_numbers,status=session['status_sel'])
                # print(data)
            columns = ['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                        'Purchase Date',"status", "Our Status",'Current Status', 'Status Update Date', 'Scheduled Delivery Date']
            total_records = len(data)
            total_pages = (total_records + records_per_page - 1) // records_per_page  # Ceiling division
            table_data_paginated = data[(current_page - 1) * records_per_page: current_page * records_per_page]
            total_records = len(data)
            total_pages = (total_records + records_per_page - 1) // records_per_page  # Ceiling division
            table_data_paginated = data[(current_page - 1) * records_per_page: current_page * records_per_page]
            df_data = [list(row) for row in data]
            df_data = pd.DataFrame(data, columns = ['Shipment Number', 'Internal Order ID', 'SKU', 'Venue', 'Order ID',
                    'Purchase Date','status' ,'Current Status', 'Status Update Date', 'Scheduled Delivery Date'])
            shipment_df = pd.DataFrame(list(shipment_data.items()), columns=['Shipment Number', 'Tag'])
            df_data = df_data.merge(shipment_df, on='Shipment Number', how='left')
            file_name = f"{session['start_date_sel'] or 'begin-to'}_{session['end_date_sel'] or session['current_date']}_{session['venue_sel'] or 'all-venues'}_{session['carrier_sel'] or 'all-carriers'}_{session['status_sel'] or "all-status"}_{session['tag_sel'] or 'all-tags'}.csv"
            session['file_name_tagged'] = file_name
            # df_data.to_csv(f"tags_files/{file_name}", index=False)

            return render_template('tag_management.html', venues=venues, carriers=carriers,shipment_data=shipment_data,data=table_data_paginated,columns=columns,current_page=current_page,total_pages=total_pages,downl=True,log_dates=log_dates)
    return render_template('tag_management.html', venues=venues, carriers=carriers,shipment_data=shipment_data,downl = False,log_dates=log_dates)




@app.route('/update_tag', methods=['POST'])
def update_tag():
    
    log_file_path = 'log_dates.json'

    # Get the form data (assuming each key is the shipment number)
    form_data = request.form

    # Get the current user from session
    current_user = session.get("user", "Unknown User")

    # Load existing logs if available
    if os.path.exists(log_file_path):
        with open(log_file_path, 'r') as log_file:
            try:
                log_dates = json.load(log_file)
            except json.JSONDecodeError:
                log_dates = {}
    else:
        log_dates = {}

    # Iterate over form data and update the data dict based on shipment numbers
    for shipment_number, new_status in form_data.items():
        # Get the current status from the existing data
        current_status = log_dates[shipment_number]['current_status']

        # Log the change only if the status is actually different
        if current_status != new_status :
            # Update the data with the new status
            log_dates[shipment_number]['current_status'] = new_status

            # Get or create the shipment entry in log_dates
            shipment_log = log_dates.get(shipment_number, {
                "current_status": current_status or "unknown",
                "log": []
            })

            # Update the shipment's log with the new status, current date-time, and user
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            shipment_log["log"].append([new_status, current_date, current_user])
            shipment_log["current_status"] = new_status

            # Store the updated log back into log_dates
            log_dates[shipment_number] = shipment_log

    # Write the updated log_dates to the JSON log file
    with open(log_file_path, 'w') as log_file:
        json.dump(log_dates, log_file, indent=4)

    

    return redirect(url_for('add_tag_manual'))



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


@app.route('/download_file_taged')
def download_file_taged():
    try:
        FILE_DIRECTORY = 'tags_files'
        # Ensure session has file_name
        if 'file_name_tagged' not in session or not session['file_name_tagged']:
            return "No file available for download", 400

        file_path = os.path.join(FILE_DIRECTORY, session['file_name_tagged'])
        print(session["file_name_tagged"])
        print(file_path)
        # Check if the file exists
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return f"File '{session['file_name_tagged']}' not found", 404

    except Exception as e:
        return f"Error occurred: {str(e)}", 500   

if __name__ == '__main__':
    
    app.run(debug=True)
