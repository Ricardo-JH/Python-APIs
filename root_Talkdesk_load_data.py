from API import API


root = API('rootinsurance')

root.API.load_data(tables='All'
                   #start_time='2023-08-31T00:00:00',
                   #end_time='2023-09-01T00:00:00',
                   #temp=True
                   )
