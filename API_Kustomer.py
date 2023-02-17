import pandas as pd
import requests
import time
from datetime import datetime, timedelta
import SQLConnection
from API_parameters import kustomer_dic


class API_Kustomer():
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.set_attributes()
    

    def set_attributes(self):
        if self.API_domain == 'kustomer':
            self.API_key = kustomer_dic['API_key']
            self.base_API = kustomer_dic['baseAPI']
            self.SQLschema = kustomer_dic['SQLschema']
            self.report_types = kustomer_dic['report_types']


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


    def get_dataReport(self, report_type, job_ID):
        df = pd.DataFrame()
        isValidResponse = False

        page = 1
        params = f'?page={page}&pageSize=100' #&sort=desc'
        
        url = f'{self.base_API}/{report_type}'

        cursor = 'init'

        url = f'{self.base_API}/{report_type}/details/jobs/{job_ID}'
        url = url.replace('users_presence', 'analytics/users')
        url = url.replace('users_routingStatus', 'analytics/users')        
        
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
                        response_field = self.responses_dict[report_type]
                        df_response = pd.DataFrame(response[response_field]).fillna('')
                    except:
                        print(f"Couldn't get results ob Job: {url_iter}")

                    for row_i in range(len(df_response.axes[0])):
                        try:
                            if report_type == 'users_presence':
                                userId = df_response['userId'].iloc[row_i]
                                row = df_response['primaryPresence'].iloc[row_i]
                            elif report_type == 'users_routingStatus':
                                userId = df_response['userId'].iloc[row_i]
                                row = df_response['routingStatus'].iloc[row_i]
                        
                            if report_type in ['users_presence', 'users_routingStatus']:
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
       
        if report_type == 'users_presence':
            df['users_presence_id'] = df['userId'] + ' ' + df['startTime'].astype(str)
        if report_type == 'users_routingStatus':
            df['users_routingStatus_id'] = df['userId'] + ' ' + df['startTime'].astype(str)
        
        # print(df)
        # print(df.query('endTime == ""'))
        df['endTime'] = df['endTime'].replace([''], [datetime.utcnow() + timedelta(minutes=-1)])
        
        return df


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


    def load_users(self):
        
        url = f'{self.base_API}/users'
        next_url = f'{self.base_API}/users'
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
        print(f'Time to get Activity Codes: {elapsedTime} Sec')
               
        print('\nFinish updating Activity Codes')


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
                response = requests.get(url, headers=headers).json()['entities']
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


    def load_schedules(self, week, op):
        
        df = pd.DataFrame()
        SQL_Table = f'[{self.SQLschema}Temp].[schedules]'
        
        if op > 1:
            SQL_Table = SQL_Table.replace('Temp', '')
        else:
            SQLConnection.truncate(SQL_Table, self.API_domain)

        LOB_list, schedule_id = self.get_LOB(week)
        i = 1
        for LOB in LOB_list:
            print(i)
            url = f'{self.base_API}/workforcemanagement/managementunits/{LOB}/weeks/{week}/schedules/{schedule_id}'

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
            i = i + 1
        SQLConnection.insert(df, SQL_Table, self.API_domain)
        print('\nFinish Loading Schedules Data')
        