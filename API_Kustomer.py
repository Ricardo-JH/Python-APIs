from API_parameters import kustomer_dic
from datetime import datetime, timedelta
import SQLConnection
import pandas as pd
import requests
import time


class API_Kustomer:
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.base_API = None
        self.search_API = None
        self.SQLschema = None
        self.report_types = None
        self.API_key = None
        self.access_token = None
        self.access_token_startTime = None
        self.set_attributes()
        

    def set_attributes(self):
        if self.API_domain == 'kustomer':
            self.search_API = kustomer_dic['searchAPI']
            self.base_API = kustomer_dic['baseAPI']
            self.SQLschema = kustomer_dic['SQLschema']
            self.report_types = kustomer_dic['report_types']
            self.API_key = kustomer_dic['API_key']


    def load_data(self, tables=None, start_time=None, end_time=None, days=1):
        SQL_tables = []

        if start_time == None:
            self.SQLschema = self.SQLschema + 'Temp'
            end_time = datetime.utcnow() + timedelta(minutes=-1)
            start_time = end_time + timedelta(days=-days)
        elif type(start_time) == str:
            start_time = datetime.fromisoformat(start_time)
            end_time = datetime.fromisoformat(end_time)

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

            # self.authorize()
            
            if 'Temp' in SQL_tables[i]:
                SQLConnection.truncate(SQL_tables[i], self.API_domain)
                hours = -8
            else:
                hours = 0

            while aux_time <= end_time and aux_time <= now:
                
                # self.authorize()
                
                print(f'\n{SQL_tables[i]} {self.API_domain}')
                print(f'Load until: {end_time + timedelta(hours=hours)}')
                print(f'Loading {aux_start_time + timedelta(hours=hours)} -> {aux_time + timedelta(hours=hours)}')
                
                df = self.get_dataReport(report_types[i], aux_start_time.strftime('%Y-%m-%dT%H:%M:%S'), aux_time.strftime('%Y-%m-%dT%H:%M:%S'))
                return
                SQLConnection.insert(df, SQL_tables[i], self.API_domain)                

                aux_start_time = aux_start_time + timedelta(days=1)
                aux_time = aux_start_time + timedelta(days=1)

        print('Finish loading Data\n')
   

    def get_dataReport(self, report_type, from_date, to_date):
        isValidResponse = False
        
        url = f'{self.search_API}?pageSize=500'
        
        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.API_key}"
        }

        payload = {
        "and": [
            { f"{report_type}_updated_at": { "gte": f"{from_date}" } },
            { f"{report_type}_updated_at": { "lte": f"{to_date}" } }
        ],
        "sort" : [{f"{report_type}_updated_at": "asc"}],
        "queryContext": f"{report_type}",
        "or":[]
        }

        start_time = time.time()
        
        while not isValidResponse:
            # try:
                response = requests.post(url, json=payload, headers=headers).json()
                time.sleep(0.5)
                               
                df_response = pd.DataFrame(response['data'])
                nest_url = response['links']['next']
                
                return
                df_entries = df_entries.loc[:, df_entries.columns != 'calls_historical_base.data_status'] #[['interaction_id', 'call_type', 'start_time', 'end_time','talkdesk_phone_number', 'customer_phone_number', 'talk_time', 'record','hangup', 'in_business_hours?', 'callback_from_queue?', 'waiting_time','agent_speed_to_answer', 'holding_time', 'rating', 'description','agent_name', 'phone_display_name', 'disposition_code', 'transfer?','handling_agent', 'tags', 'ivr_options', 'csat_score','csat_survey_time', 'team', 'rating_reason', 'agent_disconnected']]
                df = df_entries.fillna('')
                # print(df.columns)
                
                if self.API_domain == 'rootinsurance':
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
            # except:
                # print(response)
                time.sleep(0.5)
        return
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
