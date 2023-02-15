from Requests import Request
import time


root = Request('rootinsurance')

while True:
    root.load_data('All')
    time.sleep(5 * 60)
