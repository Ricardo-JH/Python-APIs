from API import API


root = API('kustomer')

root.API.load_data('All', 
                    temp=False, 
                    # offset_minutes=7*24*60, 
                    start_time='2023-01-01T00:00:00',
                    end_time='2023-03-23T00:00:00', 
                    interval_minutes=24*60)

# add more levels to depack into conversations response
# finish SQL Table with message and note data columns
# update conversation SQL Table