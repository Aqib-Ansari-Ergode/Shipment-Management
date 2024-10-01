from flask import Flask, render_template,request,redirect,send_file,url_for,session
from datetime import datetime
import SQL_functions as sqlf
import pandas as pd
import os
import csv

application = Flask(__name__)

application.secret_key = 'your_secret_key' 

@application.route('/')
def index():
    session.clear()
    session['post_done'] = False
    session['page_no'] = 1
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format the date as needed
    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()
    # Dummy inventory data for Aux Hold Cases and Warehouse Cases
    aux_hold_cases = [
        { 'delivered':list(sqlf.get_delivered()[0])[0]},
    ]

    warehouse_cases = [
        { 'quantity': 50, 'status': 'Ready to Ship'},
        { 'quantity': 100, 'status': 'Ready to Ship'},
        { 'quantity': 60, 'status': 'Packing'},
        { 'quantity': 20, 'status': 'Packing'},
        { 'quantity': 80, 'status': 'Ready to Ship'}
    ]

    return render_template('index.html', current_date=current_date, aux_hold_cases=aux_hold_cases, warehouse_cases=warehouse_cases, venues= venues,carriers=carriers)

@application.route('/get_delivered', methods=['POST'])
def handle_get_delivered():
    current_date = datetime.now().strftime("%Y-%m-%d")  # Format the date as needed

    venues = sqlf.get_venues()
    carriers = sqlf.get_carriers()
    # Get form data
    if request.method == 'post':
        session['start_date']  = request.form.get('start_date')
        session['end_date'] = request.form.get('end_date')
        session['venue'] = request.form.get('venue')
        session['carrier'] = request.form.get('carrier')
        department = request.form.get('department')
        session['post_done'] = True
        print(session['start_date'] )
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        session['page_no'] = 1
        if session['venue'] == "False":
            session['venue'] = False
        if session['carrier'] == 'False':
            session['carrier'] = False

        print(session['start_date'] )
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        # Call the function with the provided form data
        # delivered_data = sqlf.get_delivered(start=start_date, end=end_date, venue=venue, carrier=carrier, department=department)
        aux_hold_cases = [
            { 'delivered':list(sqlf.get_delivered(start=session['start_date'] , 
                                                end=session['end_date'],venue=session['venue'],
                                                carrier=session['carrier']))[0][0]},
        ]
        print(aux_hold_cases)
        # aux_hold_cases = [
        #     { 'delivered':100},
        # ]
        warehouse_cases = [
            { 'quantity': 50, 'status': 'Ready to Ship'},
            { 'quantity': 100, 'status': 'Ready to Ship'},
            { 'quantity': 60, 'status': 'Packing'},
            { 'quantity': 20, 'status': 'Packing'},
            { 'quantity': 80, 'status': 'Ready to Ship'}
        ]
    # Render a template or return the result
    else:
        session['post_done'] = False
        session['start_date']  = False
        session['end_date'] = False
        session['venue'] =False
        session['carrier'] = False
        department = request.form.get('department')
        print(session['start_date'] )
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        session['page_no'] = 1
        if session['venue'] == "False":
            session['venue'] = False
        if session['carrier'] == 'False':
            session['carrier'] = False

        print(session['start_date'] )
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        # Call the function with the provided form data
        # delivered_data = sqlf.get_delivered(start=start_date, end=end_date, venue=venue, carrier=carrier, department=department)
        aux_hold_cases = [
            { 'delivered':list(sqlf.get_delivered(start=session['start_date'] , 
                                                end=session['end_date'],venue=session['venue'],
                                                carrier=session['carrier']))[0][0]},
        ]
        print(aux_hold_cases)
        # aux_hold_cases = [
        #     { 'delivered':100},
        # ]
        warehouse_cases = [
            { 'quantity': 50, 'status': 'Ready to Ship'},
            { 'quantity': 100, 'status': 'Ready to Ship'},
            { 'quantity': 60, 'status': 'Packing'},
            { 'quantity': 20, 'status': 'Packing'},
            { 'quantity': 80, 'status': 'Ready to Ship'}
        ]
    # Render a template or return the result
    return render_template('index.html', current_date=current_date,
                            aux_hold_cases=aux_hold_cases, warehouse_cases=warehouse_cases,venues=venues,
                           start_date=session['start_date'] ,
                           end_date=session['end_date'],venue_sel=session['venue'],
                           carriers= carriers,carrier_sel = session['carrier']) 
 # Replace with your template

df = 0
@application.route('/get_delivered_details')
def get_delivered_details():
    global df
    # Sample data to be displayed in the table
    # print(start_date)
    # print(end_date)
    # print(venue)
    # print(carrier)
    # print(page_no)

    if session["post_done"]:
        if session['start_date'] == "" or session['start_date'] == None:
            session['start_date'] = False
        if session['end_date'] == "" or session['end_date'] == None:
            session['end_date'] = False
        if session['venue'] == "" or session['venue'] == None:
            session['venue'] = False
        if session['carrier'] == "" or session['carrier'] == None:
            session['carrier'] = False
        if session['page_no'] == "" or session['page_no'] == None:
            page_no = 1
        print(session['start_date'])
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        print(session['page_no'])
        table_data = sqlf.get_delivered(start=session['start_date'] ,end=session['end_date'],venue=session['venue'],carrier=session['carrier'],columns=True)
        
    else:
       
        session['start_date'] = False
        session['end_date'] = False
        session['venue'] = False
        session['carrier'] = False
        page_no = 1
        print(session['start_date'])
        print(session['end_date'])
        print(session['venue'])
        print(session['carrier'])
        print(session['page_no'])
        table_data = sqlf.get_delivered(start=session['start_date'] ,end=session['end_date'],venue=session['venue'],carrier=session['carrier'],columns=True)
        
    data = []
    for i in table_data:
        arr = []
        for j in i:
            arr.append(j)
        data.append(arr)
    df = pd.DataFrame(columns=['Shipment Number','Internal Order ID','SKU','Venue','Order ID','Purchase Date','Current Status','Status Update Date','Scheduled Delivery Date'],data=data)
    file_name = f"{session['start_date']}_{session['end_date']}_{session['venue']}_{session['carrier']}.csv"
    session['file_name'] = file_name
    table_data = table_data[25*(int(session['page_no'])-1):25*(int(session['page_no'])-1)+25]
    # print(table_data)
    df.to_csv(f"files/{session['file_name']}",index=False)
    return render_template('Delivered.html', table_data=table_data,file_name = session['file_name'])

FILE_DIRECTORY = './files/'
@application.route('/download')
def download_file():
    global df
    file_path = os.path.join("files", session['file_name'])
    
    print("File saved successfullt")
    return send_file('tags_with_order_ids.csv', as_attachment=True)
    #     return "File not found", 404
    

@application.route('/add_tag', methods=['POST'])
def add_tag():
    # Get tags from the form submission (tags is a dictionary with order_id as keys)
    # form_data = request.form.items()
    # print(form_data)
    # for i in form_data:
    #     print(i)
    # Define the file path for the CSV (you can choose your own path)
    csv_file = 'tags_with_order_ids.csv'

    # Open the CSV file in applicationend mode, and write each tag with its corresponding order_id
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
    application.run(debug=True,port=8080)
    session.clear()
    
