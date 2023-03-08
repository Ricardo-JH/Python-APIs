from API import API


ultra = API('ultra')

ultra.API.load_data(['users_presence'], temp=True, offset_minutes=12*60, interval_minutes=12*60)

