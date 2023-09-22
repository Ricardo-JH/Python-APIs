from API_parameters import therabody_dic, root_dic
from datetime import datetime, timedelta
import SQLConnection
import pandas as pd
import requests
import base64
import time


class API_Talkdesk:
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.login_API = None
        self.base_API = None
        self.client_id = None
        self.client_secret = None
        self.SQLschema = None
        self.report_types = None
        self.access_token = None
        self.access_token_startTime = None
        self.set_attributes()
        

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


    def authorize(self):    
        encodedData = base64.b64encode(bytes(f"{self.client_id}:{self.client_secret}", "ISO-8859-1")).decode("ascii")

        payload = "grant_type=client_credentials"

        headers = {
        "accept": "application/json",
        "Authorization": f"Basic {encodedData}",
        "content-type": "application/x-www-form-urlencoded"
        }

        if self.access_token_startTime == None:
            self.access_token_startTime = time.time()
            response = requests.post(self.login_API, data=payload, headers=headers)
            access_token = response.json()['access_token']
            self.access_token = access_token
        else:
            access_token_end = time.time()
            elapsed_time = access_token_end - self.access_token_startTime
            if elapsed_time > 500:
                self.access_token_startTime = None
                self.authorize()


    def load_data(self, tables=None, start_time=None, end_time=None, days=1, temp=True):
            SQL_tables = []

            if start_time == None:
                temp = True
                end_time = datetime.utcnow() + timedelta(minutes=-1)
                start_time = end_time + timedelta(days=-days)
            elif type(start_time) == str:
                start_time = datetime.fromisoformat(start_time)
                end_time = datetime.fromisoformat(end_time)
            
            if temp:
                self.SQLschema = self.SQLschema + 'Temp'

            if tables == None:
                print('No tables introduced')
                return
            elif tables == 'All':
                report_types = self.report_types
            else:
                report_types = tables

            for table in report_types:
                SQL_tables.append(f'[{self.SQLschema}].[{table}]')

            for i in range(len(SQL_tables)):
                now = datetime.utcnow()
                
                aux_start_time = start_time

                aux_time = start_time + timedelta(days=1)

                self.authorize()
                
                if 'Temp' in SQL_tables[i]:
                    SQLConnection.truncate(SQL_tables[i], self.API_domain)
                    hours = -8
                else:
                    hours = 0

                while aux_time <= end_time and aux_time <= now:
                    
                    self.authorize()
                    
                    print(f'\n{SQL_tables[i]} {self.API_domain}')
                    print(f'Load until: {end_time + timedelta(hours=hours)}')
                    print(f'Loading {aux_start_time + timedelta(hours=hours)} -> {aux_time + timedelta(hours=hours)}')
                    print(self.access_token[-10:-1])
                    
                    job = self.execute_report(report_types[i], aux_start_time.strftime('%Y-%m-%dT%H:%M:%S'), aux_time.strftime('%Y-%m-%dT%H:%M:%S'))
                    df = self.get_dataReport(report_types[i], job)
                    self.delete_report(report_types[i], job)
                    SQLConnection.insert(df, SQL_tables[i], self.API_domain)                

                    aux_start_time = aux_start_time + timedelta(days=1)
                    aux_time = aux_start_time + timedelta(days=1)

            print('Finish loading Data\n')


    def execute_report(self, report_type, from_date, to_date):

        isValidResponse = False
        
        url = f'{self.base_API}/data/reports/{report_type}/jobs'
        
        payload = {"format": "json",
                    "Name": "TestReport",
                    "timespan": {
            "from": from_date,
            "to": to_date
            }
        }
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        start_time = time.time()
        
        while not isValidResponse:
            try:
                response = requests.post(url, json=payload, headers=headers).json()
                time.sleep(0.5)
                job_ID = response['job']['id']
                isValidResponse = True
                
            except:
                time.sleep(0.5)
        
        elapsedTime = time.time() - start_time
        print(f'Time to Execute Report: {elapsedTime} Sec')
        
        return job_ID
    

    def get_dataReport(self, report_type, job_ID):
        isValidResponse = False
        
        url = f'{self.base_API}/data/reports/{report_type}/files/{job_ID}'
        
        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        start_time = time.time()
        
        while not isValidResponse:
            response = requests.get(url.replace('files', 'jobs'), headers=headers).json()

            if 'entries' in response.keys():

                try:
                    response = requests.get(url, headers=headers).json()
                except:
                    print('Error requesting... trying again.')
                    time.sleep(1)

                df_entries = pd.DataFrame(response['entries'])
                df_entries = df_entries.loc[:, df_entries.columns != 'calls_historical_base.data_status'] #[['interaction_id', 'call_type', 'start_time', 'end_time','talkdesk_phone_number', 'customer_phone_number', 'talk_time', 'record','hangup', 'in_business_hours?', 'callback_from_queue?', 'waiting_time','agent_speed_to_answer', 'holding_time', 'rating', 'description','agent_name', 'phone_display_name', 'disposition_code', 'transfer?','handling_agent', 'tags', 'ivr_options', 'csat_score','csat_survey_time', 'team', 'rating_reason', 'agent_disconnected']]
                df = df_entries.fillna('')
                
                if self.API_domain == 'rootinsurance':
                    try:
                        if report_type == 'user_status':
                            df['user_status_id'] = df['user_id'] + ' ' + df['status_start_at'].astype(str)
                        if report_type == 'adherence':
                            df['adherence_id'] = df['agent_name'] + ' ' + df['adherence_event_start_time'].astype(str)
                        if report_type == 'feedback_flow':
                            df.rename(columns= {'ring\xa0group': 'ring group'}, inplace=True)

                    except KeyError as e:
                        print(response)

                isValidResponse = True
            else:
                try:
                    print(response['job']['status'], sep='  ', end=' ', flush=True)
                except:
                    print(f'\nError getting Job status. Response: {response}')
                    
                    self.authorize()
                    headers['Authorization'] = f"Bearer {self.access_token}"
                    
                    print('Authorized and running again...')
                    time.sleep(0.5)
        
        elapsedTime = time.time() - start_time
        print(f'\nTime to get Data Report: {elapsedTime} Sec')
        return df


    def delete_report(self, report_type, job_ID=None):

        self.authorize()

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        # delete a job if specified
        if job_ID:
            url = f'{self.base_API}/data/reports/{report_type}/files/{job_ID}'
            try:
                requests.delete(url, headers=headers)
                print(f'Job ID {job_ID} deleted')
            except Exception as e:
                print(f'Job ID {job_ID} could not be deleted')
                print(f'{e.__class__} occurred{e}')
        
        # delete all jobs of a type
        else:
            url = f'{self.base_API}/data/reports/{report_type}/jobs'
            while url:
                # print(url)
                response = requests.get(url, headers=headers).json()
                df_response = pd.DataFrame(response['_embedded']['jobs'])
                
                df_response = df_response.query('status != "deleted"')

                for i in range(len(df_response.index)):
                    job_ID = df_response.iloc[i]['id']
                    self.delete_report(report_type, job_ID)

                try:
                    url = response['_links']['next']['href']
                except:
                    url = None
    

    def load_users(self):
        try:
            url = f'{self.base_API}/users'
            SQL_Table = f'[{self.SQLschema}].[users]'
            last_page = False

            SQLConnection.truncate(SQL_Table, self.API_domain)

            while not last_page:

                self.authorize()
            
                headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {self.access_token}"
                }
                
                start_time = time.time()
                isValidResponse = False

                while not isValidResponse:
                    try:

                        response = requests.get(url, headers=headers).json()
                        time.sleep(1)

                        df = pd.DataFrame(response).fillna('')
                        df_users = pd.DataFrame(df['_embedded']['users'])[['id', 'email', 'name', 'active', 'gender', 'extension', 'external_phone_number', 'created_at', 'ring_groups']]
                        df_users['ring_groups'] = df_users['ring_groups'].map(str).str.replace('[', '').str.replace(']', '')
                        df_users['extension'] = df_users['extension'].map(str)

                        try:
                            url = df['_links']['next']['href']
                        except KeyError as KeyErr:
                            url = None
                            time.sleep(0.5)

                        SQLConnection.insert(df_users, SQL_Table, self.API_domain)
                        isValidResponse = True
                        
                    except:
                        time.sleep(0.5)
                        elapsedTime = time.time() - start_time

                elapsedTime = time.time() - start_time
                print(self.access_token[-10:-1])
                print(f'Time to get Users Data: {elapsedTime} Sec')
                
                if url == None:
                    last_page = True
            
            print('\nFinish Updating Users Data')

            return 0
        except:
            return 1

        
