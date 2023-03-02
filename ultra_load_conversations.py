from API import API


ultra = API('ultra')

ultra.API.load_data(['conversations'], temp=True, offset_minutes=1440/2, interval_minutes=1440/2)

