import base64
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import SQLConnection
from API_parameters import *

class API:
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.login_API = None
        self.base_API = None
        self.client_id = None
        self.client_secret = None
        self.SQLschema = None
        self.report_types = None
        self.access_token = None
        self.access_token_start = None
        self.API_key = None
        self.set_attributes()



    def set_API(self):
        if self.API_domain in ['therabody', 'rootinsurance']:
            self.API = API_Talkdesk(self.API_domain)
        elif self.API_domain == 'ultra':
            self.API = API_Genesys(self.API_domain)
        elif self.API_domain == 'kustomer':
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




    def set_attributes(self):
        if self.API_domain == 'therabody':
            self.login_API = therabody_dic['loginAPI'].replace('API_domain', self.API_domain)
            self.base_API = therabody_dic['baseAPI']
            self.SQLschema = therabody_dic['SQLschema']
            self.client_id = therabody_dic['clientID']
            self.client_secret = therabody_dic['client_secret']
            self.report_types = therabody_dic['report_types']
        
        if self.API_domain == 'rootinsurance':
            self.login_API = root_dic['loginAPI'].replace('API_domain', self.API_domain)
            self.base_API = root_dic['baseAPI']
            self.SQLschema = root_dic['SQLschema']
            self.client_id = root_dic['clientID']
            self.client_secret = root_dic['client_secret']
            self.report_types = root_dic['report_types']
            
        if self.API_domain == 'ultra':
            self.login_API = ultra_dic['loginAPI']
            self.base_API = ultra_dic['baseAPI']
            self.SQLschema = ultra_dic['SQLschema']
            self.client_id = ultra_dic['clientID']
            self.client_secret = ultra_dic['client_secret']
            self.report_types = ultra_dic['report_types']
        
        if self.API_domain == 'kustomer':
            self.API_key = kustomer_dic['API_key']
            self.base_API = ultra_dic['baseAPI']
            self.SQLschema = ultra_dic['SQLschema']
            self.report_types = ultra_dic['report_types']


    def authorize(self):    
        encodedData = base64.b64encode(bytes(f"{self.client_id}:{self.client_secret}", "ISO-8859-1")).decode("ascii")

        payload = "grant_type=client_credentials"

        headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encodedData}",
        "content-type": "application/x-www-form-urlencoded"
        }

        if self.API_domain == 'ultra':
            self.access_token = 'EjNwULC3ithDWT2mSaom9akk90c1uVskozCETALHySP5H4gcKnloj8okkLbfTI_ypvFFibdz9TerBU4wL2LYnw'
        
        elif self.access_token_start == None:
            self.access_token_start = time.time()
            response = requests.post(self.login_API, data=payload, headers=headers)
            access_token = response.json()['access_token']
            self.access_token = access_token

        else:
            access_token_end = time.time()
            elapsed_time = access_token_end - self.access_token_start
            if elapsed_time > 500:
                self.access_token_start = None
                self.authorize()

    
    def load_data(self, API, SQL_table, report_type, start_date, end_date):
        now = datetime.utcnow()

        if type(start_date) == str:
            start_date = datetime.fromisoformat(start_date)
            end_date = datetime.fromisoformat(end_date)

        aux_datetime = start_date + timedelta(days=1)

        self.authorize()
        
        if 'Temp' in SQL_table:
            SQLConnection.truncate(SQL_table, self.API_domain)
            hours = -8
        else:
            hours = 0

        while aux_datetime <= end_date and aux_datetime <= now:
            
            self.authorize()
            
            print(f'\n{SQL_table} {self.API_domain}')
            print(f'Load until: {end_date + timedelta(hours=hours)}')
            print(f'Loading {start_date + timedelta(hours=hours)} -> {aux_datetime + timedelta(hours=hours)}')
            print(self.access_token[-10:-1])
            
            job = API.execute_report(report_type, start_date.strftime('%Y-%m-%dT%H:%M:%S'), aux_datetime.strftime('%Y-%m-%dT%H:%M:%S'))
            df = API.get_dataReport(report_type, job)
            API.delete_report(report_type, job)
            SQLConnection.insert(df, SQL_table, self.API_domain)                

            start_date = start_date + timedelta(days=1)
            aux_datetime = start_date + timedelta(days=1)
