from API import API
import time


ultra = API('ultra')

while True:
    ultra.API.load_data('All')
    time.sleep(5 * 60)
