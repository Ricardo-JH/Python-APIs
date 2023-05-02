from API import API


ultra = API('ultra')

ultra.API.load_data(['users_presence'], 
                    temp=True,
                    offset_minutes='max', 
                    # start_time='2023-03-01T00:00:00',
                    # end_time='2023-03-16T00:00:00', 
                    # interval_minutes=24*60
                    )

