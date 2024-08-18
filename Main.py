from API import API
import time


ultra = API('ultra')

# ultra.API.load_users()
# ultra.API.load_schedules_activityCodes()
# ultra.API.load_data(['conversations'], True, interval_minutes=24*60, \
                    #  start_time='2023-03-05T00:00:00', end_time='2023-03-08T00:00:00')

ultra.API.load_evaluations()

# while True:
    # root.API.load_data('All')
    # time.sleep(5 * 60)



'''
    Add time variations from hours to days.
    Change Insert method7
    Set Intert after getting the report
'''
