from API import API
import time


ultra = API('ultra')

# ultra.API.load_users()
# ultra.API.load_schedules_activityCodes()
ultra.API.load_data(['conversations'], True, offset_minutes=1440, interval_minutes=1440)


# while True:
    # root.API.load_data('All')
    # time.sleep(5 * 60)



'''
    Add time variations from hours to days.
    Change Insert method7
    Set Intert after getting the report
'''
