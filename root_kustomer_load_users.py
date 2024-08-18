from API import API


root = API('kustomer')

root.API.load_users()
root.API.load_teams()
root.API.load_queues()