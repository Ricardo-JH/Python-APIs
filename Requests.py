from API  import API_Talkdesk
from API  import API_Genesys
from datetime import datetime, timedelta

class Request:
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.API = None
        self.set_API()


    def set_API(self):
        if self.API_domain in ['therabody', 'rootinsurance']:
            self.API = API_Talkdesk(self.API_domain)
        elif self.API_domain == 'ultra':
            self.API = API_Genesys(self.API_domain)


    def load_data(self, tables=None, start_time=None, end_time=None, days=1):
        SQL_tables = []
        schema = self.API.SQLschema

        if start_time == None:
            temporal = True
            end_time = datetime.utcnow() + timedelta(minutes=-1)
            start_time = end_time + timedelta(days=-days)
        else:
            temporal = False

        if temporal:
            schema = schema + 'Temp'
        
        if tables == 'All':
            report_types = self.API.report_types
        else:
            report_types = tables

        for table in report_types:
            SQL_tables.append(f'[{schema}].[{table}]')

        for i in range(len(SQL_tables)):
            self.API.load_data(self.API, SQL_tables[i], report_types[i], start_time, end_time)

        print('Finish loading Data\n')
    

    def load_users(self):
        self.API.load_users()


    def load_schedules(self, op=1):
        
        # self.API.load_schedules_activityCodes
        
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        for i in range(op):
            self.API.load_schedules(start_of_week, op)
            start_of_week = start_of_week - timedelta(days=7)
        
    
    # def load_users_data(self):
    #     self.API.load_users_data()
