from API import API


root = API('rootinsurance')

root.API.load_data(tables='All',
                #    start_time='2023-08-28T18:00:00',
                #    end_time='2023-08-29T18:00:00',
                #    temp=True
                   )
