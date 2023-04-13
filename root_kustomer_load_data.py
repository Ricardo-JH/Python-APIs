from API import API


root = API('kustomer')

root.API.load_data('All', 
                    temp=True, 
                    # start_time='2023-01-01T00:00:00',
                    # end_time='2023-04-13T00:00:00', 
                    offset_minutes='max'
                    # offset_minutes=24*60, 
                    # interval_minutes=24*60
                    )

