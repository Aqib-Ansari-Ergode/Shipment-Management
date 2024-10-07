import mysql.connector
from mysql.connector import Error
import pandas as pd

# Connection global variable to allow reuse
connection = None

def create_connection(host_name, user_name, user_password, db_name):
    """
    Creates a connection to the MySQL database and returns the connection object.
    """
    global connection
    try:
        if connection is None or not connection.is_connected():
            connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name,
            pool_name='mypool',
            pool_size=30,  # Adjust this based on your application's concurrency
            autocommit=True,
        )

            if connection.is_connected():
                print("Connection to MySQL DB successful")
        else:
            print("Using existing database connection")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection

def reconnect_if_needed():
    global connection
    if connection is None or not connection.is_connected():
        print("Reconnecting to MySQL DB...")
        connection = create_connection("54.187.97.21", "aqib_ro", "mka@efew8743ICNMmcskCS", "ergodeap_media")
    else:
        try:
            connection.ping(reconnect=True, attempts=3, delay=5)
        except Error as e:
            print(f"Reconnection attempt failed: {e}")
            connection = create_connection("54.187.97.21", "aqib_ro", "mka@efew8743ICNMmcskCS", "ergodeap_media")

def execute_query(query):
    global connection
    reconnect_if_needed()  # Ensure the connection is alive
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        print("Query executed successfully")
    except mysql.connector.Error as e:
        if e.errno in (mysql.connector.errorcode.CR_SERVER_LOST, 
                       mysql.connector.errorcode.CR_SERVER_GONE_ERROR):
            print("Lost connection to MySQL server, trying to reconnect...")
            reconnect_if_needed()
            return execute_query(query)  # Retry the query
        else:
            print(f"The error '{e}' occurred")


def fetch_query_results(query):
    """
    Fetches the results of a query.
    """
    global connection
    reconnect_if_needed()  # Ensure the connection is alive

    cursor = connection.cursor()
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"The error '{e}' occurred")
        return None

# Connect to MySQL database
connection = create_connection("media-master.ergodeapps.com", "aqib_ro", "mka@efew8743ICNMmcskCS", "ergodeap_media")

# # Example of creating a table
# create_table_query = """
# CREATE TABLE IF NOT EXISTS employees (
#     id INT AUTO_INCREMENT PRIMARY KEY,
#     name VARCHAR(100),
#     age INT,
#     gender VARCHAR(10),
#     salary DECIMAL(10, 2)
# );
# """
# execute_query(connection, create_table_query)

# # Example of inserting data
# insert_employee_query = """
# INSERT INTO employees (name, age, gender, salary)
# VALUES
# ('John Doe', 28, 'Male', 70000.00),
# ('Jane Smith', 32, 'Female', 80000.00);
# """
# execute_query(connection, insert_employee_query)

# Example of fetching data
def get_delivered(start=False, end=False, venue=False, carrier=False, department=False, columns=False):
    if columns:
        select_employees_query = '''SELECT 
        od.shipment_no, od.internal_order_id , od.sku, od.venue, 
        om.order_id, om.purchase_date, 
        otd.current_status , otd.status_update_date, otd.scheduled_delivery_date 
        FROM order_details AS od 
        JOIN order_mast AS om ON od.order_mast_id = om.order_mast_id 
        JOIN order_tracking_details AS otd ON od.order_detail_id = otd.order_detail_id 
        WHERE otd.is_auxhold_tracking = 1 
        AND otd.current_status LIKE '%delivered%' '''
    else:
        select_employees_query = '''SELECT COUNT(otd.tracking_id) 
            FROM order_details AS od 
            JOIN order_mast AS om ON od.order_mast_id = om.order_mast_id 
            JOIN order_tracking_details AS otd ON od.order_detail_id = otd.order_detail_id 
            WHERE otd.is_auxhold_tracking = 1 
            AND otd.current_status LIKE '%delivered%' '''

    # Date filtering
    if start and end:
        select_employees_query += f"AND om.purchase_date BETWEEN '{start}' AND '{end}' "

    # Venue filtering
    if venue:
        select_employees_query += f"AND od.venue = '{venue}' "

    # Carrier filtering
    if carrier:
        select_employees_query += f"AND otd.carrier_name = '{carrier}' "

    # Department filtering


    # select_employees_query += "LIMIT 5;"
    
    delivered = fetch_query_results(query=select_employees_query+"limit 100")  # Use your own DB query function
    return delivered

def get_data(start=False, end=False, venue=False, carrier=False, department=False):
    
    select_employees_query = '''SELECT 
        od.shipment_no, od.internal_order_id , od.sku, od.venue, 
        om.order_id, om.purchase_date, 
        od.status,otd.current_status , otd.status_update_date, otd.scheduled_delivery_date 
        FROM order_details AS od 
        JOIN order_mast AS om ON od.order_mast_id = om.order_mast_id 
        JOIN order_tracking_details AS otd ON od.order_detail_id = otd.order_detail_id 
        '''
    
    where1 = 0

    # Date filtering
    if start and end :
        if where1==0:
            select_employees_query += "where "
            where1 = 1
            select_employees_query += f"  om.purchase_date BETWEEN '{start}' AND '{end}' "
        else:
            select_employees_query += " and "
            select_employees_query += f"  om.purchase_date BETWEEN '{start}' AND '{end}' "

    # Venue filtering
    if venue:
        if where1 == 0:
            select_employees_query += " where"
            select_employees_query += f"  od.venue = '{venue}' "
            where1 = 1
        else:
            select_employees_query+=' and '
            select_employees_query+=f" od.venue = '{venue}'"

    # Carrier filtering
    if carrier:
        if where1 == 0:
            select_employees_query += ' where '
            select_employees_query += f"  otd.carrier_name = '{carrier}' "
            where1 = 1
        else:
            select_employees_query += ' and '
            select_employees_query += f"  otd.carrier_name = '{carrier}' "

    # Department filtering


    # select_employees_query += "LIMIT 5;"
    
    data = fetch_query_results(query=select_employees_query+''' and om.ship_country NOT IN ('USA' , 'United States',  'usa','U.S.A.','UNITED STATES','USA','US') order by od.internal_order_id desc limit 100  ''')  # Use your own DB query function
    return data


# delivered = get_delivered(venue="GM-Germany")
# for i in delivered:
#     print(i)

def get_venues():
    venues = fetch_query_results(query='select distinct venue from order_details;')

    venues_list = []
    for i in venues:
        for j in i:
            venues_list.append(j)
    # print(venues_list)
    return venues_list

def get_carriers():
    
    carriers = fetch_query_results(query='select distinct carrier_name from order_tracking_details;')

    carrier_list = []
    for i in carriers:
        for j in i:
            carrier_list.append(j)
    # print(venues_list)
    return carrier_list

# print(get_carriers())
# Close the connection
def close_Mysql_con():
    if connection.is_connected():
        connection.close()
        print("MySQL connection is closed")

# close_Mysql_con()

if __name__=="__main__":
    deli = get_delivered(start='2024-08-01',end='2024-09-30',venue='GM-Spain',carrier='USPS',columns=True)
    data = []
    for i in deli:
        arr = []
        for j in i:
            arr.append(j)
        data.append(arr)
    df = pd.DataFrame(columns=['Internal Order ID','SKU','Venue','Order ID','Purchase Date','Current Status','Status Update Date','Scheduled Delivery Date'],data=data)
    df.to_csv('test_USPS.csv',index=False)
