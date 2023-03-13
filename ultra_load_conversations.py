from API import API


ultra = API('ultra')

ultra.API.load_data(['conversations'], temp=True, offset_minutes=12*60, interval_minutes=12*60)

