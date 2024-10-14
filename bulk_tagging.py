import csv
import json
import ast
import os
import pandas as pd
from datetime import datetime
# Function to read the CSV file and convert it to JSON
def csv_to_json(csv_file_path, json_file_path):
    # Check if the JSON file exists
    # if os.path.exists(json_file_path):
    #     with open(json_file_path, mode='r', encoding='utf-8') as json_file:
    #         # Load existing data
    #         existing_data = json.load(json_file)
    # else:
    #     existing_data = {}

    # with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
    #     csv_reader = csv.DictReader(csv_file)
    #     for row in csv_reader:
    #         shipment_no = row['shipment_no']
    #         if existing_data[shipment_no]['current_status'] != current_status:
    #             log = existing_data[shipment_no]["log"].append(ast.literal_eval(row['log']))
    #             current_status = row['current_status']
    #          # Safely evaluate the string representation of the list

    #         # Update existing data or add new entry
    #             existing_data[shipment_no] = {
    #                 'current_status': current_status,
    #                 'log': log
    #             }
    #         else:
    #             current_status = row['current_status']
    #             log = ast.literal_eval(row['log']) 
    #             existing_data[shipment_no] = {
    #             'current_status': current_status,
    #             'log': log
    #         }
    df_bulk = pd.read_csv(csv_file_path)
    df_bulk
    current_user = "Bulk (file)"
    if os.path.exists(json_file_path):
        with open(json_file_path, 'r') as log_file:
            try:
                log_dates = json.load(log_file)
            except json.JSONDecodeError:
                log_dates = {}
    else:
        log_dates = {}

    # Update logs based on form data
    for i in range(len(df_bulk)):
       

        if df_bulk['shipment_no'][i] not in log_dates:
            
            shipment_log = {
                "current_status": df_bulk['new_status'][i] or "unknown",
                "log": [[df_bulk['new_status'][i], datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_user]]
            }
            log_dates[df_bulk['shipment_no'][i]] = shipment_log
        else:
            current_status = log_dates[df_bulk['shipment_no'][i]]['current_status']
            if current_status != df_bulk['new_status'][i]:
                log_dates[df_bulk['shipment_no'][i]]['current_status'] = df_bulk['new_status'][i]
                current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_dates[df_bulk['shipment_no'][i]]["log"].append([df_bulk['new_status'][i], current_date, current_user])


           

    # Write the updated JSON data to a file
    with open(json_file_path, mode='w', encoding='utf-8') as json_file:
        json.dump(log_dates, json_file, indent=4)

if __name__=="__main__":
    # Example usage
    csv_file_path = 'uploads/test2_tag.csv'  # Path to your input CSV file
    json_file_path = 'test_tagging.json'  # Path to save the output JSON file
    csv_to_json(csv_file_path, json_file_path)

    print(f"Converted {csv_file_path} to {json_file_path}")
