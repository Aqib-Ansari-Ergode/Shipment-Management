from datetime import datetime
import json
import os
import pandas as pd
import SQL_functions as sqlf

def load_data(filename):
    if os.path.exists(filename):
        with open(filename, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    else:
        return {}

# Assuming `get_data` is fetching data from a database

def Update_sql_tag():
    data_sql = sqlf.get_data()
    data_sql_clip = []
    columns = [
        'shipment_no', 'internal_order_id', 'sku', 'venue', 'order_id', 'purchase_date',
        'status', 'current_status', 'status_update_date', 'scheduled_delivery_date'
    ]

    df_sql = pd.DataFrame(data_sql, columns=columns)

    filename = "log_dates.json"
    data_json = load_data(filename)
    df_list = []

    for order_id, order_data in data_json.items():
        df_list.append({
            'shipment_no': order_id,
            'log': order_data['log'],
            'current_status': order_data['current_status']
        })

    df_json = pd.DataFrame(df_list)
    merged_df = pd.merge(df_sql, df_json, on="shipment_no", how='left')
    merged_df.drop_duplicates(subset='shipment_no', keep='first',inplace=True)
    merged_df.reset_index(drop=True,inplace=True)
    print(len(merged_df))
    for i, current_status_x in zip(range(len(merged_df)), merged_df['current_status_x']):
        print(i)
        # print(merged_df['log'][i],current_status_x)
        last = ''
        if type(merged_df['log'][i]) == list:
            for j in merged_df['log'][i]:
                last = ""
                if j[2] == "sql":
                    last = j[0]
        print("1 - \n",merged_df)
        print(type(merged_df.at[i,'log']))
        print(current_status_x != last)
        if current_status_x != last:
                if type(merged_df.at[i,'log']) == list:
                    # print("2 - \n",merged_df)
                    
                        merged_df.at[i,'log'].append([current_status_x,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'sql'])
                        merged_df.at[i,'current_status_y'] = current_status_x
                
                else:
                    merged_df.at[i,'log'] = [[current_status_x,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'sql']]
                    merged_df.at[i,'current_status_y'] = current_status_x



    data = {}
    # print("4 - \n",merged_df)
    for i in merged_df[['shipment_no', 'current_status_y', 'log']].values:
        shipment_no, curr_status, log_val = i
        log_val = log_val if isinstance(log_val, list) else [['NA', "NA", "NA"]]
        curr_status = curr_status if isinstance(curr_status, str) else "NA"
        data[shipment_no] = {
            "current_status": curr_status,
            'log': log_val
        }
    # print("5 - \n",merged_df)


    log_file_path = 'log_dates.json'
    with open(log_file_path, 'w') as log_file:
        json.dump(data, log_file, indent=4)

if __name__=="__main__":
    Update_sql_tag()