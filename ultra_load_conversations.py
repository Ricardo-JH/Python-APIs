from API import API


ultra = API('ultra')

ultra.API.load_data(['conversations'], 
                    temp=True,
                    # start_time='2023-04-27T00:00:00',
                    # end_time='2023-04-27T12:00:00', 
                    # offset_minutes='max'
                    offset_minutes='max' 
                    # interval_minutes=24*60
                    )
