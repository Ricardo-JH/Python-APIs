from API import API
import time


ultra = API('ultra')

# ultra.API.load_users()
# ultra.API.load_schedules_activityCodes()
ultra.API.load_data(['conversations'], '2023-02-20T00:00:00', '2023-02-23T00:00:00')


# while True:
    # root.API.load_data('All')
    # time.sleep(5 * 60)
