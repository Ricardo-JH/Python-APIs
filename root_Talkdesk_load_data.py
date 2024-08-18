from API import API


root = API('rootinsurance')

root.API.load_data(tables='All'
                  #  ,start_time='2024-04-23T07:00:00'
                  #  ,end_time='2024-04-25T07:00:00'
                  #  ,temp=True
                   )
