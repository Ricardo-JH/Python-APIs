import pandas as pd
import pyodbc
import time


def select(API_domain, query): 
    start_time = time.time()

    if API_domain == 'therabody':
        Database = 'DbTherabody'
    elif API_domain in ['rootinsurance', 'kustomer']:
        Database = 'RootInsurance'
    elif API_domain == 'ultra':
        Database = 'Ultra'

    Driver = 'ODBC Driver 17 for SQL Server'
    Server = 'SQLSERVER\GGAMASTEDDB'
    User = 'GGASOLUTIONS\ricardo.jaramillo'
    Connection_String = f'DRIVER={Driver};SERVER={Server};DATABASE={Database};UID={User};Trusted_Connection=yes;'

    connection = pyodbc.connect(Connection_String)

    data = pd.DataFrame(pd.read_sql(query, connection)).fillna('')
    # data = data[['Emp', 'schedule_referenceDate_TRESS', 'schedule_daily_Genesys']]
    
    elapsedTime = time.time() - start_time
    print(f'Time get data: {elapsedTime} sec')
    print(data)

    connection.close()
    return data


def insert(dataFrame, SQL_Table, API_domain, columns=None): 
    global cursor

    start_time = time.time()

    # select only columns in the SQL table
    if columns != None:
        active_columns = [i for i in columns if i in dataFrame.columns]
        dataFrame = dataFrame[active_columns]
    
    if API_domain == 'therabody':
        Database = 'DbTherabody'
    elif API_domain in ['rootinsurance', 'kustomer']:
        Database = 'RootInsurance'
    elif API_domain == 'ultra':
        Database = 'Ultra'
    
    Driver = 'ODBC Driver 17 for SQL Server'
    Server = 'SQLSERVER\GGAMASTEDDB'
    # Database = 'RootInsurance'
    User = 'GGASOLUTIONS\ricardo.jaramillo'

    Connection_String = f'DRIVER={Driver};SERVER={Server};DATABASE={Database};UID={User};Trusted_Connection=yes;'# PWD={Password};

    # Trusted Connection to Named Instance
    connection = pyodbc.connect(Connection_String)
    cursor=connection.cursor()

    insert_into = ''
    var_values = ''
    list_values = []

    len_DataFrame_columns = len(dataFrame.columns)
    
    for index in range(len_DataFrame_columns):
        insert_into = insert_into + f'[{dataFrame.columns[index]}]'
        var_values = var_values + '?'

        if index + 1 < len_DataFrame_columns:
            insert_into = insert_into + ', '
            var_values = var_values + ', '
    
    query = f'INSERT INTO {SQL_Table} ({insert_into}) Values({var_values})'
    
    # createTable(SQL_Table, dataFrame)

    for index, row in dataFrame.iterrows():
        for i in range(len_DataFrame_columns):
            if i < len_DataFrame_columns:
                list_values.append(row[i])
                # print(f'Item: {dataFrame.columns[i]}. Value: {row[i]}. Actual Len: {len(str(row[i]))}')
        # print(query)
        # print(list_values)
        # dataFrame.to_csv('conv.csv')
        cursor.execute(query, list_values)

        list_values = []
    
    elapsedTime = time.time() - start_time
    # print(f'Time to insert Data Report: {elapsedTime} Sec') 
    # print('Successfull Data insertion')

    connection.commit()
    cursor.close()
    connection.close()


def truncate(SQL_Table, API_domain): 
    global cursor
    if API_domain == 'therabody':
        Database = 'DbTherabody'
    elif API_domain in ['rootinsurance', 'kustomer']:
        Database = 'RootInsurance'
    elif API_domain == 'ultra':
        Database = 'Ultra'

    Driver = 'ODBC Driver 17 for SQL Server'
    Server = 'SQLSERVER\GGAMASTEDDB'
    # Database = 'RootInsurance'
    User = 'GGASOLUTIONS\ricardo.jaramillo'
    Password = 'Ab12345*'

    Connection_String = f'DRIVER={Driver};SERVER={Server};DATABASE={Database};UID={User};PWD={Password};Trusted_Connection=yes;'

    # Trusted Connection to Named Instance
    connection = pyodbc.connect(Connection_String)
    cursor=connection.cursor()
    
    query = f'Truncate Table {SQL_Table}'
    
    cursor.execute(query)

    connection.commit()
    cursor.close()
    connection.close()