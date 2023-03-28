from API import API


root = API('kustomer')

root.API.load_data('All', 
                    temp=False, 
                    # offset_minutes=7*24*60, 
                    start_time='2023-03-24T00:00:00',
                    end_time='2023-03-28T00:00:00', 
                    interval_minutes=24*60)

