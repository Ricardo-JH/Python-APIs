from API import API
import time


root = API('rootinsurance')

while True:
    root.API.load_data('All')
    time.sleep(5 * 60)
