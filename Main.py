from API import API
import time


ultra = API('ultra')

# ultra.API.load_users()
# ultra.API.load_schedules_activityCodes()
ultra.API.load_data(['conversations'], True, interval_minutes=2880, start_time='2023-02-28T20:00:00', end_time='2023-03-02T20:00:00')


# while True:
    # root.API.load_data('All')
    # time.sleep(5 * 60)



'''
    Add time variations from hours to days.
    Change Insert method7
    Set Intert after getting the report
'''
