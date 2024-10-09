import json
import os
from datetime import datetime
import pandas as pd
# with open('log_dates.json', 'r') as file:
#     json_data = json.load(file)


# # Print the current status and log entries
# for key, value in json_data.items():
#     for j in zip(value['log']):
#         print(key ," -> ",j)
#     print("--"*20)

# # import json

# # Sample data to be written to a JSON file
# data_to_write = {
#     "C1649742": {
#         "current_status": "PA - Delivered",
#         "log": [
#             [
#                 "PA - In Process",
#                 "2024-10-08 12:12:29",
#                 "sql"
#             ]]
#     }
# }

# # # Specify the filename
# filename = 'log_dates.json'


    
key = 'C1643567'
# with open(filename, 'w') as file:
#         json.dump(data, file, indent=4)

# log_file_path = 'log_dates.json'

#     # Load existing logs if available
# if os.path.exists(log_file_path):
#         with open(log_file_path, 'r') as log_file:
#             try:
#                 log_dates = json.load(log_file)
                
#             except json.JSONDecodeError:
#                 log_dates = {}
# else:
#         log_dates = {}

# # log_dates = load_data(filename=log_file_path)
# data_json = ""


# log_dates["C1649742"]
# print(log_dates["C1649742"])
# for i in log_dates:
#         print(log_dates[i]["current_status"])

def load_data(filename):
    # Check if the file exists
    if os.path.exists(filename):
        # Load the existing data from the JSON file
        with open(filename, 'r') as file:
            existing_data = json.load(file)
            return existing_data
    else:
        # If the file doesn't exist, start with an empty dictionary
        existing_data = {}
        return existing_data

import SQL_functions as sqlf

data_sql = sqlf.get_data()
data_sql_clip = []
columns = [
    'shipment_no', 'internal_order_id', 'sku', 'venue', 'order_id', 'purchase_date', 
    'status', 'current_status', 'status_update_date', 'scheduled_delivery_date'
]

# Create the DataFrame
df_sql = pd.DataFrame(data_sql, columns=columns)
     
print(df_sql.head())




     
filename = "log_dates.json"
data_json = load_data(filename=filename)
df_list = []
for order_id, order_data in data_json.items():
    # for log_entry in order_data['log']:
        df_list.append({
            'shipment_no': order_id,
            'log': order_data['log'],
            'current_status': order_data['current_status']
        })

df_json = pd.DataFrame(df_list)
# print(df_json)
# for i in range(len(df_json['log'][0])):
    # print(df_json['log'][0][i])


merged_df = pd.merge(df_sql,df_json,on="shipment_no", how='left')
merged_df_c = merged_df[['shipment_no','current_status_x','log']]
# print(merged_df_c.tail())
last_log = merged_df['log'].copy()
for i,z in zip(range(len(merged_df['log'])),merged_df['current_status_x']):
    last = ""
    # print(type(merged_df['log'][i]) == list)
    if type(merged_df['log'][i]) == list:
        for j in merged_df['log'][i]:
            if j[-1] == 'sql':
                last = j
                # print(last)
                # print(j[-1])
        # print("--"*20)
    else:
         last = merged_df['log'][i]
        #  print(i)
    # print(last ,"->",z)
    if last != z and z != None:
        if type(merged_df['log'][i]) == list:
            merged_df.at[i,'log'].append([z,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'sql'])
            merged_df.at[i,'current_status_y'] = z
        else:
            merged_df.at[i,"log"] = [[z,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),'sql']]
            merged_df.at[i,'current_status_y'] = z
            # pass

# for i,j in zip(last_log,merged_df['log']):
    # if type(i) == list:
    #     print(i[-1],' -> ',j[-1])
    #     print('--'*20)
    # else:
    #     print(i, "->" , j)
    #     print('--'*20)

data = {}
for i in merged_df.iloc[:,[0,-1,-2]].values:
    # print(i[2])\
    if type(i[2])  == list:
         log_val = i[2]
    else:
         log_val = [['NA',"NA","NA"]]
    data[i[0]] = {
            "current_status" : 'PA - Delivered' if i[1]=='Delivered' else "PA - In transit",
            'log' : log_val
        }

json_data1 = json.dumps(data, indent=4)
print(json_data1)
log_file_path = 'log_dates.json'
with open(log_file_path, 'w') as log_file:
        json.dump(data, log_file, indent=4)

# # for i in 
# print(merged_df_c['log'][0][-1][-1],merged_df['current_status_x'][0])


# print(data_json)

# for i,j in zip(data_sql,data_json):
#     last = ""
#     for k in data_json[j]['log']:
        
#         if k[2] == "sql":
#             last = k[0]
#             print(k[2])
    
#     # print(i[7],data_json[j]["current_status"])

#     if i[7] != last and i[7] != None :
#         if i[7] != 'Delivered':
#                 data_json[j]['current_status'] = "In Transit to Logistic"
#                 data_json[j]['log'].append(["In Transit to Logistic",datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"sql"])
#                 # print(data_json[j]['log'])
#         else:
#                 data_json[j]['current_status'] = i[7]
#                 data_json[j]['log'].append([i[7],datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"sql"])
#                 # print(data_json[j]['log'])

#     print("--"*20)

# with open(filename, 'w') as file:
#     json.dump(data_json, file, indent=4)

# new_status= "PA - Aqib Updat"
# data = load_data(filename=filename)
# if key in data:
#     print( data[key])


# # #  for writeing 
# if key in data:
#     last = ""
#     print([i for i in data[key]['log']])
#     for i in [i for i in data[key]['log']]:
#          if i[2] == "sql":
#               last = i[0]
    
#     if last != new_status:
         
#         data[key]['current_status'] = new_status
#         data[key]['log'].append([new_status,datetime.now().strftime("%Y-%m-%d %H:%M:%S"),"sql"])
# else:
#      data[key] = {
#             "current_status": "test",
#             "log": [["test", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sql"]]
#         }
# print(data[key])
