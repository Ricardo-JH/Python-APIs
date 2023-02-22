from datetime import datetime, timedelta
from API_parameters import ultra_dic
import SQLConnection
import pandas as pd
import numpy as np
import requests
import base64
import time


class API_Genesys():
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
        if self.API_domain == 'ultra':
            self.login_API = ultra_dic['loginAPI']
            self.base_API = ultra_dic['baseAPI']
            self.SQLschema = ultra_dic['SQLschema']
            self.client_id = ultra_dic['clientID']
            self.client_secret = ultra_dic['client_secret']
            self.report_types = ultra_dic['report_types']


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
            #response = requests.post(self.login_API, data=payload, headers=headers)
            #access_token = response.json()['access_token']
            #self.access_token = access_token
            self.access_token = 'AFdWRYvGn0oXFYTq7BraKAYfh3rRDWTKR0PqvjEwkjq5vEaHSnvwke3ipHSs_DjT7So8qfKeWRGQSO_GLj3etA'

        else:
            access_token_end = time.time()
            elapsed_time = access_token_end - self.access_token_startTime
            if elapsed_time > 500:
                self.access_token_startTime = None
                self.authorize()


    def depack_json(self, json, base=pd.DataFrame()):
        try:
            df_lv0 = pd.DataFrame(json)
        except ValueError:
            df_lv0 = pd.DataFrame(pd.json_normalize(json))

        columns_containing_json = []
        columns_containing_list = []

        if not base.empty:
            for column in base.columns:
                df_lv0[column] = base[column].iloc[0]
        
        print(df_lv0)

        # get columns containing json and list data
        for column in df_lv0.columns:
            first_element = df_lv0[column].iloc[0]
            if type(first_element) == dict:
                columns_containing_json.append(column)
            if type(first_element) == list:
                columns_containing_list.append(column)
        
        df_lv0_base = df_lv0[np.setdiff1d(df_lv0.columns, columns_containing_json + columns_containing_list)][0:1]

        if len(columns_containing_list) > 0:
            # access to every list
            for column_list in columns_containing_list:
                df_column_containing_list = df_lv0[column_list]
                # print(df_column_containing_list)
                
                for lis_in_column in df_column_containing_list:#df_lv2.shape[0]):
                    # print(lis_in_column)
                    for element_in_lis_in_column_containing_list in lis_in_column:
                        if type(element_in_lis_in_column_containing_list) == str:
                            print(pd.DataFrame({column_list: element_in_lis_in_column_containing_list}, index=[0]))
                        elif type(element_in_lis_in_column_containing_list) == dict:
                            df = self.depack_json(element_in_lis_in_column_containing_list)
                        else:
                            print('nor a list or dict')
                            print(type(element_in_lis_in_column_containing_list))
        
        if len(columns_containing_json) > 0:
            # access to every json
            # print(json)
            # print(df_lv0)
            # print(columns_containing_json)
            for column_json in columns_containing_json:
                # print(column_json)
                # print(df_lv0[column_json])
                # print(df_lv0[column_json].shape[0])
                # print(df_lv0[column_json].iloc[0])
                # print(type(df_lv0[column_json]))
                # print(type(df_lv0[column_json].iloc[0]))
                for serie in df_lv0[column_json]:
                    df = self.depack_json(serie)
                print('after depack')
        return df


    def get_LOB(self, week):
        LOB_list = []

        url = f'{self.base_API}/workforcemanagement/businessunits/84b495aa-7cdf-4921-b848-913e5f5f0506/weeks/{week}/schedules'
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

                response = response['entities']
                time.sleep(0.5)
                schedule_id = pd.DataFrame(response)['id'].iloc[0]

                response = requests.get(f'{url}/{schedule_id}', headers=headers).json()['managementUnits']
                
                for dict in response:
                    LOB_list.append(dict['managementUnit']['id'])
                # print(LOB_list)

                isValidResponse = True
            except:
                time.sleep(0.5)
                elapsedTime = time.time() - start_time

        elapsedTime = time.time() - start_time
        print(self.access_token[-10:-1])
        print(f'Time to get LOBs: {elapsedTime} Sec')

        return LOB_list, schedule_id


    def execute_jobId(self, report_type, from_date, to_date):

        isValidResponse = False
        
        url = f'{self.base_API}/analytics/{report_type}/details/jobs'
        url = url.replace('users_presence', 'users')
        
        payload = {"format": "json",
                    "Name": "TestReport",
                    "interval": f"{from_date}/{to_date}"
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
                job_ID = response['jobId']
                isValidResponse = True
                
            except:
                time.sleep(0.5)
        
        elapsedTime = time.time() - start_time
        print(f'Time to Execute Report: {elapsedTime} Sec')
        
        return job_ID
    

    def delete_report(self, report_type, job_ID):

        url = f'{self.base_API}/{report_type}/details/jobs/{job_ID}'
        url = url.replace('users_presence', 'analytics/users')
        url = url.replace('users_routingStatus', 'analytics/users')

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        try:
            requests.delete(url, headers=headers)
            print(f'Job ID {job_ID} deleted\n')
        except Exception as e:
            print(f'Job ID {job_ID} could not be deleted\n')
            print(f'{e.__class__} occurred\n{e}')

    
    def load_schedules_activityCodes(self):
        df = pd.DataFrame()

        url = f'{self.base_API}/workforcemanagement/businessunits/84b495aa-7cdf-4921-b848-913e5f5f0506/activitycodes'
        SQL_Table = f'[{self.SQLschema}].[activityCodes]'
        
        SQLConnection.truncate(SQL_Table, self.API_domain)

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
                time.sleep(0.5)
                df = pd.DataFrame(response['entities']).fillna('')
                df = df[['id', 'name', 'active', 'defaultCode', 'category', 'lengthInMinutes', 'countsAsPaidTime', 'countsAsWorkTime', 'agentTimeOffSelectable', 'countsTowardShrinkage', 'plannedShrinkage', 'interruptible']]#.reset_index(drop=True).fillna('')
                # print(df)
                SQLConnection.insert(df, SQL_Table, self.API_domain)
                isValidResponse = True
            except Exception as e:
                time.sleep(0.5)
                elapsedTime = time.time() - start_time
                print(f'Exception: {e} \nElapsed Time: {elapsedTime}')

        elapsedTime = time.time() - start_time
        print(self.access_token[-10:-1])
        print(f'Time to update Activity Codes: {elapsedTime} Sec')
               
        print('\nFinish updating Activity Codes')


    def load_schedules(self, op=1):
        
        # self.API.load_schedules_activityCodes
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        for i in range(op):
            
            df = pd.DataFrame()
            SQL_Table = f'[{self.SQLschema}Temp].[schedules]'
            
            if op > 1:
                SQL_Table = SQL_Table.replace('Temp', '')
            else:
                SQLConnection.truncate(SQL_Table, self.API_domain)
            
            aux_start_of_week = start_of_week
            LOB_list, schedule_id = self.get_LOB(aux_start_of_week)
            
            j = 1
            
            for LOB in LOB_list:
                print(j)
                url = f'{self.base_API}/workforcemanagement/managementunits/{LOB}/weeks/{aux_start_of_week}/schedules/{schedule_id}'

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
                        
                        if pd.DataFrame(response).empty:
                            break

                        time.sleep(0.5)
                        
                        df_schedules = pd.DataFrame(response['result'])[['id', 'weekDate', 'description', 'published', 'userSchedules']].fillna('').iloc[5:]
                        # print(df_schedules)
                        df_schedules = df_schedules.reset_index().rename(columns={'index': 'userId', 'id': 'scheduleId'})
                        
                        for schedule_i in range(len(df_schedules.axes[0])):
                            df_schedule_info = df_schedules[['userId', 'scheduleId', 'weekDate', 'description', 'published']].iloc[schedule_i: schedule_i + 1].reset_index(drop=True)
                            shifts = df_schedules['userSchedules'].iloc[schedule_i]['shifts']

                            for shift in shifts:
                                df_shift = pd.DataFrame(shift)
                                df_schedule_info['referenceDate'] = df_shift['startDate']
                                df_activities = df_shift['activities']

                                for activity_i in range(len(df_activities.axes[0])):
                                    activity = df_activities.iloc[activity_i]
                                    df_activity = pd.DataFrame(activity, index=[0])[['activityCodeId', 'startDate', 'lengthInMinutes', 'countsAsPaidTime']]
                                    result = pd.concat([df_schedule_info, df_activity], axis=1, join='inner')
                                    df = pd.concat([result, df.loc[:]]).reset_index(drop=True).fillna('')
                                    # print(df)
                    
                        # print(df)
                        
                        isValidResponse = True
                    except:
                        time.sleep(0.5)
                        elapsedTime = time.time() - start_time

                elapsedTime = time.time() - start_time
                print(self.access_token[-10:-1])
                print(f'Time to get Schedule {LOB}: {elapsedTime} Sec')
                j = j + 1
            SQLConnection.insert(df, SQL_Table, self.API_domain)
            print('\nFinish Loading Schedules Data')
            
            aux_start_of_week = aux_start_of_week - timedelta(days=7)


    def load_users(self):
        
        url = f'{self.base_API}/users'
        next_url = f'{self.base_API}/users?pageSize=500'
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
                    # print(url)
                    print(next_url)
                    response = requests.get(next_url, headers=headers).json()
                    time.sleep(1)
                    # print(response)
                    df = response['entities']
                    df_users = pd.DataFrame(df)[['id', 'name', 'email', 'state', 'username', 'version', 'acdAutoAnswer']].fillna('')#
                    # df_users['ring_groups'] = df_users['ring_groups'].map(str).str.replace('[', '').str.replace(']', '')
                    # df_users['extension'] = df_users['extension'].map(str)
                    # print(df_users)
                    try:
                        next_url = response['nextUri']
                    except KeyError as KeyErr:
                        next_url = None
                        time.sleep(0.5)

                    SQLConnection.insert(df_users, SQL_Table, self.API_domain)
                    isValidResponse = True
                    
                except:
                    time.sleep(0.5)
                    elapsedTime = time.time() - start_time

            elapsedTime = time.time() - start_time
            print(self.access_token[-10:-1])
            print(f'Time to get Users Data: {elapsedTime} Sec')
            
            if next_url == None:
                last_page = True
            else:
                next_url = url.replace('/api/v2/users', next_url)

        print('\nFinish Updating Users Data')


    def load_usersPresence(self, report_type, SQL_table, from_date, to_date):
        job = self.execute_jobId(report_type, from_date, to_date)
        url = f'{self.base_API}/analytics/users/details/jobs/{job}'
        
        df = pd.DataFrame()
        isValidResponse = False
        cursor = 'init'

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        start_time = time.time()

        while not isValidResponse:
            while cursor != '':
                try:
                    job_status = requests.get(url, headers=headers).json()
                    time.sleep(1)
                except Exception as e:
                    print(f"'Couldn't retrieve Job\n{e}")

                if job_status['state'] == 'FULFILLED':
                    
                    if cursor != 'init':
                        url_iter = f'{url}/results?cursor={cursor}'
                    else:
                        url_iter = f'{url}/results'
                    
                    try:
                        response = requests.get(url_iter, headers=headers).json()
                        df_response = pd.DataFrame(response['userDetails']).fillna('')
                    except:
                        print(f"Couldn't get results ob Job: {url_iter}")

                    for row_i in range(len(df_response.axes[0])):
                        try:
                            if report_type == 'users_presence':
                                userId = df_response['userId'].iloc[row_i]
                                row = df_response['primaryPresence'].iloc[row_i]
                        
                                for dict in row:
                                    dict['userId'] = userId
                                    new_row = pd.DataFrame(dict, index=[0])
                                    df = pd.concat([new_row, df.loc[:]]).reset_index(drop=True).fillna('')
                        except:
                            print(f'row {row_i}\nCould not be loaded')
                    
                    try:
                        cursor = response['cursor']
                    except:
                        cursor = ''
            isValidResponse = True

        elapsedTime = time.time() - start_time
        print(f'Time to get Data Report: {elapsedTime} Sec')
       
        df['users_presence_id'] = df['userId'] + ' ' + df['startTime'].astype(str)
        df['endTime'] = df['endTime'].replace([''], [datetime.utcnow() + timedelta(minutes=-1)])

        SQLConnection.insert(df, SQL_table, self.API_domain)
        self.delete_report(report_type, job)


    def load_conversations(self, report_type, SQL_table, from_date, to_date):
        # job = self.execute_jobId(report_type, from_date, to_date)
        job = 'c7ec7db8-65f8-4cdc-a1f2-d114db9fe7ee'
        url = f'{self.base_API}/analytics/conversations/details/jobs/{job}'
        
        df = pd.DataFrame()
        isValidResponse = False
        cursor = 'init'

        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        start_time = time.time()

        while not isValidResponse:
            while cursor != '':
                try:
                    job_status = requests.get(url, headers=headers).json()
                    time.sleep(1)
                except Exception as e:
                    print(f"'Couldn't retrieve Job\n{e}")

                if job_status['state'] == 'FULFILLED':
                    
                    if cursor != 'init':
                        url_iter = f'{url}/results?cursor={cursor}'
                    else:
                        url_iter = f'{url}/results'
                    
                # try:
                    response = requests.get(url_iter, headers=headers).json()
                    response = self.depack_json(response)
                    return
                    df_response = pd.DataFrame(response['conversations']).fillna('')
                # except:
                    
                    print(f"Couldn't get results ob Job: {url_iter}")
                    return
                    for row_i in range(len(df_response.axes[0])):
                        try:
                            if report_type == 'users_presence':
                                userId = df_response['userId'].iloc[row_i]
                                row = df_response['primaryPresence'].iloc[row_i]
                        
                                for dict in row:
                                    dict['userId'] = userId
                                    new_row = pd.DataFrame(dict, index=[0])
                                    df = pd.concat([new_row, df.loc[:]]).reset_index(drop=True).fillna('')
                        except:
                            print(f'row {row_i}\nCould not be loaded')
                    
                    try:
                        cursor = response['cursor']
                    except:
                        cursor = ''
            return
            isValidResponse = True
        return
        elapsedTime = time.time() - start_time
        print(f'Time to get Data Report: {elapsedTime} Sec')
       
        df['users_presence_id'] = df['userId'] + ' ' + df['startTime'].astype(str)
        df['endTime'] = df['endTime'].replace([''], [datetime.utcnow() + timedelta(minutes=-1)])

        SQLConnection.insert(df, SQL_table, self.API_domain)
        self.delete_report(report_type, job)


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

                from_date = aux_start_time.strftime('%Y-%m-%dT%H:%M:%S')
                to_date = aux_time.strftime('%Y-%m-%dT%H:%M:%S')

                if report_types[i] == 'users_presence':
                    self.load_usersPresence(report_types[i], SQL_tables[i], from_date, to_date)
                if report_types[i] == 'conversations':
                    self.load_conversations(report_types[i], SQL_tables[i], from_date, to_date)

                aux_start_time = aux_start_time + timedelta(days=1)
                aux_time = aux_start_time + timedelta(days=1)

        print('Finish loading Data\n')
    

        


