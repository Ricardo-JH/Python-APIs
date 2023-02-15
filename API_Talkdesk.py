import base64
import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import SQLConnection
from API_parameters import *
from API import API


class API_Talkdesk(API):
    def __init__(self, API_domain):
        super().__init__(API_domain)


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
            try:
                response = requests.get(url, headers=headers).json()
                time.sleep(0.5)
                df_entries = pd.DataFrame(response['entries'])
                df_entries = df_entries.loc[:, df_entries.columns != 'calls_historical_base.data_status'] #[['interaction_id', 'call_type', 'start_time', 'end_time','talkdesk_phone_number', 'customer_phone_number', 'talk_time', 'record','hangup', 'in_business_hours?', 'callback_from_queue?', 'waiting_time','agent_speed_to_answer', 'holding_time', 'rating', 'description','agent_name', 'phone_display_name', 'disposition_code', 'transfer?','handling_agent', 'tags', 'ivr_options', 'csat_score','csat_survey_time', 'team', 'rating_reason', 'agent_disconnected']]
                df = df_entries.fillna('')
                # print(df.columns)
                
                try:
                    if report_type == 'user_status':
                        df['user_status_id'] = df['user_id'] + ' ' + df['status_start_at'].astype(str)
                    if report_type == 'adherence':
                        df['adherence_id'] = df['agent_name'] + ' ' + df['adherence_event_start_time'].astype(str)
                    if report_type == 'feedback_flow':
                        df.rename(columns= {'ring\xa0group': 'ring group'}, inplace=True)
                    # print(df)
                    # print(df.columns)
                except KeyError as e:
                    pass

                isValidResponse = True
            except:
                # print(response)
                time.sleep(0.5)
        
        elapsedTime = time.time() - start_time
        print(f'Time to get Data Report: {elapsedTime} Sec')
        return df


    def delete_report(self, report_type, job_ID):

        url = f'{self.base_API}/data/reports/{report_type}/files/{job_ID}'

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        try:
            requests.delete(url, headers=headers)
            print(f'Job ID {job_ID} deleted')
        except Exception as e:
            print(f'Job ID {job_ID} could not be deleted')
            print(f'{e.__class__} occurred{e}')


    def load_users(self):
        
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
