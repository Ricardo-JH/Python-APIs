from API import API


ultra = API('ultra')

ultra.API.load_data(['conversations'], 
                    temp=True, 
                    # offset_minutes=7*24*60, 
                    start_time='2023-04-17T00:00:00',
                    end_time='2023-04-26T00:00:00', 
                    interval_minutes=24*60)
