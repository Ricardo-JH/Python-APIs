from API import API
import time


kustomer = API('kustomer')

# ultra.API.load_users()
# ultra.API.load_schedules_activityCodes()
kustomer.API.load_data('All')

# while True:
    # root.API.load_data('All')
    # time.sleep(5 * 60)
