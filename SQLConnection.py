import pyodbc


def insert(dataFrame, SQL_Table, API_domain, fromTemp='No'): 
    global cursor
    if API_domain == 'therabody':
        Database = 'DbTherabody'
    elif API_domain == 'rootinsurance':
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
        cursor.execute(query, list_values)

        list_values = []
    print('Successfull Data insertion')

    connection.commit()
    cursor.close()
    connection.close()


def truncate(SQL_Table, API_domain): 
    global cursor
    if API_domain == 'therabody':
        Database = 'DbTherabody'
    elif API_domain == 'rootinsurance':
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