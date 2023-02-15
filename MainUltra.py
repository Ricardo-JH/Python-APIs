from Requests import Request
import time


ultra = Request('ultra')

while True:
    ultra.load_data('All')
    time.sleep(5 * 60)
