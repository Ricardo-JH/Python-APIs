from API import API


ultra = API('ultra')

ultra.API.load_users(['active', 'inactive'])
ultra.API.load_LOB()