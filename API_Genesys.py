from datetime import datetime, timedelta, date
from API_parameters import ultra_dic
from warnings import simplefilter
import SQLConnection
import pandas as pd
import numpy as np
import requests
import base64
import time
import csv


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


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
            response = requests.post(self.login_API, data=payload, headers=headers)
            access_token = response.json()['access_token']
            self.access_token = access_token
            # self.access_token = 'WzV5BnlPGsJKB-uaxI1WpGakPiSBI1rMn6SjCpq54t1QKhoJbIWgPqgRg0qhF73G-KPAyaybVYrs01Zhxo6qTg'

        else:
            access_token_end = time.time()
            elapsed_time = access_token_end - self.access_token_startTime
            if elapsed_time > 500:
                self.access_token_startTime = None
                self.authorize()


    def create_table(self, df=pd.DataFrame(), table_name='file'):
        # set replacements
        dict_rep = {"<class 'str'>": 'str', "<class 'float'>": 'float', "<class 'numpy.bool_'>": 'bit', "<class 'bool'>": 'bit'}
        columns = []

        # get list of types
        columns_type = [str(type(df[column].iloc[0])) for column in df.columns]
        columns_type = [dict_rep .get(item, item) for item in columns_type]
        
        # get max lengths
        lens = np.vectorize(len)(df.values.astype(str)).max(axis=0)
        # lens = [df[column].astype(str).str.len().max() for column in df]

        # set table code
        pos = 1
        for column, typ, length in (zip(df.columns, columns_type, lens)):
            if typ == 'str':
                columns.append(f'[{column}] nvarchar({length})' )
            else: 
                columns.append(f'[{column}] {str(typ)}')
            if pos < len(columns_type):
                columns[-1] = columns[-1] + ','
            pos += 1
        
        # show and save in a file
        df_columns = pd.DataFrame(data={"columns": columns})#.drop_duplicates(['columns'])
        df_columns.to_csv(f"./{table_name}_SQL.csv", sep='\\', header=False, index=False, quoting=csv.QUOTE_NONE, escapechar="\\", doublequote=False)
        # print(df_columns)


    def depack_json(self, json, filters=dict(), columns_to_depack=dict(), lis_df=[]):
        # convert json to DataFrame
        try:
            df_lv0 = pd.DataFrame(json).fillna('')
        except ValueError:
            df_lv0 = pd.DataFrame(pd.json_normalize(json)).fillna('')
        except Exception as e:
            pass
        # print(df_lv0)

        # get columns containing json and list data
        columns_containing_json = []
        columns_containing_list = []
        columns_to_explode = []

        for column in df_lv0.columns:
            for i in range(df_lv0[column].shape[0]):
                element = df_lv0[column].iloc[i]
                # print(column, ' ', element)
                if type(element) == list:
                    columns_containing_list.append(column)
                    break
                if type(element) == dict:
                    columns_containing_json.append(column)
                    break

        # Convert List to values / Pass list to columns_containing_json
        if len(columns_containing_list) > 0:
            # access to every column containing list
            for column_list in columns_containing_list:
                has_one_item = True
                
            
                for i in range(df_lv0[column_list].shape[0]):
                    if len(df_lv0[column_list].iloc[i]) > 1:
                        id = columns_to_depack.get(column_list)
                        # check if column is asked to be exploded
                        if id != '':
                            has_one_item = False
                            columns_to_explode.append(column_list)
                            break
                        # column doesnt need to be exploded. Get first item
                        # else:
                        #     print(len(df_lv0[column_list].iloc[i]))
                        #     print(df_lv0[column_list].iloc[i])
                if has_one_item:
                    df_lv0[column_list] = df_lv0[column_list].explode(column_list)


        # print(columns_containing_json)
        # convert Json to values
        if len(columns_containing_json) > 0:
            for column_json in columns_containing_json:
                
                json_df = pd.DataFrame(df_lv0[column_json].map(dict).values.tolist()).fillna('')
                
                # sort columns
                json_df = json_df.reindex(sorted(json_df.columns), axis=1)

                # drop duplicated columns
                columns = json_df.columns.str.lower().str.strip()
                duplicate_columns = json_df.columns[columns.duplicated()]
                # print(duplicate_columns)
                json_df.drop(columns=duplicate_columns, inplace=True)
                df_lv0.drop(columns=[column_json], inplace=True)

                for column in json_df.columns:
                    df_lv0[f'{column_json}.{column}'] = json_df[column]
        
        
        # filter data
        active_filters = [i for i in filters.keys() if i in df_lv0.columns]
        if any(active_filters):
            for filter in active_filters:
                df_lv0 = df_lv0[df_lv0[filter] == filters[filter]]

        # explode to Json values
        active_columns_to_explode = [i for i in columns_to_explode if i in columns_to_depack.keys()]
        if any(active_columns_to_explode):
            for column_json in active_columns_to_explode:
                id = columns_to_depack[column_json]
                df_remain = df_lv0.loc[:, ~df_lv0.columns.isin([column_json])]
                df_to_explode = df_lv0[id + [column_json]]
                lis_df.insert(0, df_remain)
                df_lv0 = df_to_explode.explode(column_json).reset_index(drop=True)
        
        # check if still needs cleansing
        columns_containing_json = []
        columns_containing_list = []

        active_columns_to_explode = [i for i in columns_to_depack.keys() if i in df_lv0.columns]
        for column in active_columns_to_explode:
            first_element = df_lv0[column].iloc[0]
            if type(first_element) == list:
                columns_containing_list.append(column)
            if type(first_element) == dict:
                columns_containing_json.append(column)
        
        # df_lv0.to_csv('data.csv')

        if any(columns_containing_json + columns_containing_list):
            df_lv0, lis_df = self.depack_json(df_lv0, filters, columns_to_depack, lis_df)
        
        return df_lv0, lis_df


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
                self.authorize()
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
        self.authorize()

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
                self.authorize()
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
        self.authorize()
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
                self.authorize()
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


    def load_schedules(self, week=None, week_offset=0):
            # self.API.load_schedules_activityCodes
            SQL_Table = f'[{self.SQLschema}Temp].[schedules]'
            weekdate_end = datetime.date(datetime.now()) - timedelta(days=datetime.now().weekday())

            if week == None:
                weekdate = datetime.date(datetime.now()) - timedelta(days=datetime.now().weekday()) - timedelta(days=week_offset*7)
                SQLConnection.truncate(SQL_Table, self.API_domain)
            else:
                weekdate = datetime.strptime('2023-W' + str(week - week_offset) + '-1', '%G-W%V-%u').strftime('%Y-%m-%d')
                weekdate = datetime.date(datetime.strptime(weekdate, '%Y-%m-%d'))
                SQL_Table = SQL_Table.replace('Temp', '')
            
            week = weekdate.isocalendar()[1]
            aux_start_of_week = weekdate

            # print(type(weekdate))
            # print(type(weekdate_end))

            while aux_start_of_week <= weekdate_end:
                
                df = pd.DataFrame()
                
                print(f'{SQL_Table} - Week {week} {aux_start_of_week}')
                LOB_list, schedule_id = self.get_LOB(aux_start_of_week)
                
                for LOB in LOB_list:
                    # print(j)
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
                            self.authorize()
                            response = requests.get(url, headers=headers).json()
                            
                            if pd.DataFrame(response).empty:
                                break

                            time.sleep(0.5)
                            
                            df_schedules = pd.DataFrame(response['result'])[['id', 'weekDate', 'description', 'published', 'userSchedules']].fillna('').iloc[5:]
                            # print(df_schedules)
                            df_schedules = df_schedules.reset_index().rename(columns={'index': 'userId', 'id': 'scheduleId'})
                            
                            for schedule_i in range(len(df_schedules.axes[0])):
                                df_schedule_info = df_schedules[['userId', 'scheduleId', 'weekDate', 'description', 'published']].iloc[schedule_i: schedule_i + 1].reset_index(drop=True)
                                df_schedule_info['LOB'] = LOB
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
                    print(f'Time to get Schedule {LOB}: {elapsedTime} Sec')
                SQLConnection.insert(df, SQL_Table, self.API_domain)
                print('\nFinish Loading Schedules Data')
                
                aux_start_of_week = aux_start_of_week + timedelta(days=7)
                week += 1


    def load_LOB(self):
        url = f'{self.base_API}/workforcemanagement/managementunits'
        SQL_Table = f'[{self.SQLschema}].[users_LOB]'

        SQLConnection.truncate(SQL_Table, self.API_domain)

        self.authorize()
        
        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, headers=headers).json()

        cur_page = response['pageNumber']
        pages = response['pageCount']

        start_time = time.time()
        print(SQL_Table)

        while cur_page <= pages:

            self.authorize()
            headers['Authorization'] = f"Bearer {self.access_token}"
            response = requests.get(url, headers=headers).json()

            df_LOB = response['entities']
            df_LOB = pd.DataFrame(df_LOB)[['id', 'name']].fillna('')
            
            for i in range(df_LOB.shape[0]):
                LOB_id = df_LOB['id'].iloc[i]
                LOB_name = df_LOB['name'].iloc[i]

                self.authorize()
                headers['Authorization'] = f"Bearer {self.access_token}"
                response = requests.get(f'{url}/{LOB_id}/users', headers=headers).json()

                df_LOB_users = pd.DataFrame(response['entities'])
                
                if not df_LOB_users.empty:
                    df_LOB_users.rename(columns={'id': 'userId'}, inplace=True)
                    
                    df_LOB_users['id'] = LOB_id
                    df_LOB_users['name'] = LOB_name
                    df_LOB_users = df_LOB_users[['id', 'name', 'userId']]
                else:
                    df_LOB_users = pd.DataFrame(columns=['id', 'name', 'userId'])
                    df_LOB_users.loc[len(df_LOB_users)] = [LOB_id, LOB_name, '']
                    print(f'{LOB_name} empty')

                SQLConnection.insert(df_LOB_users, SQL_Table, self.API_domain)
            cur_page += 1
        
        elapsedTime = time.time() - start_time
        print(f'Time to get Users LOB Data: {elapsedTime} Sec')
            
        print('\nFinish Updating Users LOB Data')
        

    def load_queues(self):
        url = f'{self.base_API}/routing/queues'
        SQL_Table = f'[{self.SQLschema}].[queues]'
        queues = {'mediaSettings': 'id',
                  'mediaSettings.call': '',
                  'mediaSettings.call.serviceLevel': ''}

        SQLConnection.truncate(SQL_Table, self.API_domain)
        SQLConnection.truncate(SQL_Table.replace('queues', 'users_queues'), self.API_domain)

        self.authorize()
        
        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        response = requests.get(url, headers=headers).json()
        
        cur_page_queue = response['pageNumber']
        pages_queue = 1
        pageSize_queue = 500
        pageSize_queue_users = 100

        start_time = time.time()
        print(SQL_Table)
        print(f'Total: {pages_queue}')

        while cur_page_queue <= pages_queue:

            self.authorize()
            headers['Authorization'] = f"Bearer {self.access_token}"
            
            response = requests.get(f'{url}?pageSize={pageSize_queue}&pageNumber={cur_page_queue}', headers=headers).json()
            df_queues, _ = self.depack_json(response['entities'], columns_to_depack=queues, lis_df=[])
            print(df_queues)
            SQLConnection.insert(df_queues, SQL_Table, self.API_domain, columns=ultra_dic['dict_columns']['queues'])
            
            elapsedTime = time.time() - start_time
            print(f'Time to load Queues: {elapsedTime} Sec')
            
            for i in range(df_queues.shape[0]):
                Queue_id = df_queues['id'].iloc[i]
                Queue_name = df_queues['name'].iloc[i]

                self.authorize()
                headers['Authorization'] = f"Bearer {self.access_token}"
                
                next_url = f'{url}/{Queue_id}/members?pageSize={pageSize_queue_users}&pageNumber=1'
                
                while next_url:
                    response = requests.get(next_url, headers=headers).json()
                    df_queue_users = pd.DataFrame(response['entities'])
                    
                    if not df_queue_users.empty:
                        df_queue_users.rename(columns={'id': 'userId'}, inplace=True)
                        
                        df_queue_users['id'] = Queue_id
                        df_queue_users['name'] = Queue_name
                        df_queue_users = df_queue_users[['id', 'name', 'userId']]
                    else:
                        df_queue_users = pd.DataFrame(columns=['id', 'name', 'userId'])
                        df_queue_users.loc[len(df_queue_users)] = [Queue_id, Queue_name, '']
                        # print(f'{Queue_name} empty')
                    
                    SQLConnection.insert(df_queue_users, SQL_Table.replace('queues', 'users_queues'), self.API_domain)
                    
                    try:
                        next_url = url.replace('/api/v2/routing/queues', response['nextUri'])
                    except:
                        next_url = False
                
                elapsedTime = time.time() - start_time
                print(f'Time to load users Queue {Queue_name} data: {elapsedTime} Sec')
            cur_page_queue += 1
            
        print('\nFinish Updating Users LOB Data')
        

    def load_users(self, agent_state):
        SQL_Table = f'[{self.SQLschema}].[users]'
        SQLConnection.truncate(SQL_Table, self.API_domain)
        
        for state in agent_state:
            url = f'{self.base_API}/users?state={state}&pageSize=500&pageNumber=1'

            start_time = time.time()

            self.authorize()
            headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.access_token}"
            }
            
            response = requests.get(url, headers=headers).json()
            
            pageCount = response['pageCount']
            pageNumber = response['pageNumber']
            pageSize = 500

            print(f'Total: {pageCount}')

            while pageNumber <= pageCount:
                try:
                    self.authorize()
                    headers['Authorization'] = f"Bearer {self.access_token}"
                    
                    print(pageNumber, sep='  ', end=' ', flush=True)
                    
                    url = f'{self.base_API}/users?state={state}&pageSize={pageSize}&pageNumber={pageNumber}'
                    response = requests.get(url, headers=headers).json()

                    df_users = pd.DataFrame(response['entities'])[['id', 'name', 'email', 'state', 'username', 'version', 'acdAutoAnswer']].fillna('')
                    
                    SQLConnection.insert(df_users, SQL_Table, self.API_domain)
                    
                    pageNumber += 1

                except Exception as e:
                    print(f'Error on page {pageNumber}. {e}')
                    break
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get {state} Users Data: {elapsedTime} Sec')
            
        print('\nFinish Updating Users Data')


    def load_usersPresence_jobID(self, report_type, SQL_table, from_date, to_date):
        
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
                    self.authorize()
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
        
        self.delete_report(report_type, job)

        if 'Temp' in SQL_table: 
            SQLConnection.truncate(SQL_table, self.API_domain)

        SQLConnection.insert(df, SQL_table, self.API_domain)

    
    def load_usersPresence(self, SQL_table, from_date, to_date, offset_minutes):
        userDetails = {
            'primaryPresence': ['userId']
        }
        
        url = f'{self.base_API}/analytics/users/details/query'
        
        now = datetime.utcnow()
        
        self.authorize()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        payload = {
            "interval": f"{from_date}/{to_date}",
            "presenceFilters": [
                {
                    "type": "or",
                    "predicates": [
                        {
                            "dimension": "systemPresence",
                            "value": "AVAILABLE"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "AWAY"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "BREAK"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "BUSY"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "MEAL"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "ON_QUEUE"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "TRAINING"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "IDLE"
                        },
                        {
                            "dimension": "systemPresence",
                            "value": "MEETING"
                        }
                    ]
                }
            ],
            "paging": {
                "pageSize": 100,
                "pageNumber": 1
            },
            "order": "asc"
        }
        
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers).json()
        
        pages = round(response['totalHits'] / 100)
        print(pages)
        cur_page = 1

        while pages > 0 and cur_page <= pages:
            self.authorize()
            headers['Authorization'] = f"Bearer {self.access_token}"

            print(cur_page, sep='  ', end=' ', flush=True)
            response = requests.post(url, json=payload, headers=headers).json()
            df_usersPresence, _ = self.depack_json(response['userDetails'], columns_to_depack=userDetails, lis_df=[])

            df_usersPresence['users_presence_id'] = df_usersPresence['userId'] + ' ' + df_usersPresence['primaryPresence.startTime'].astype(str)
            df_usersPresence['primaryPresence.endTime'] = df_usersPresence['primaryPresence.endTime'].replace([''], [now + timedelta(minutes=-1)])

            SQLConnection.insert(df_usersPresence, SQL_table, self.API_domain, columns=ultra_dic['dict_columns']['users_presence'])

            cur_page += 1
            payload['paging']['pageNumber'] = str(cur_page)

        print('\n')
    
        elapsedTime = time.time() - start_time
        print(f'Total Time to load Data Report: {elapsedTime} Sec')


    def load_conversations(self, SQL_table, end_time, from_date, to_date, offset_minutes):
        url = f'{self.base_API}/analytics/conversations/details/query'

        metrics = {
            'participants': ['conversationId'], 
            'participants.sessions': '', 
            'participants.sessions.metrics': ['conversationId', 'participants.participantId'], 
        }
        
        segments = {
            'participants': ['conversationId'], 
            'participants.sessions': '', 
            'participants.sessions.segments': ['conversationId', 'participants.participantId']
        }

        self.authorize()
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}"
        }

        offset_30days = (end_time + timedelta(days=-28)).strftime('%Y-%m-%dT%H:%M:%S')
        end_time = end_time.strftime('%Y-%m-%dT%H:%M:%S')
        
        tables = [pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()]
        names = ['conversations_segments', 'conversations_metrics', 'conversations_participants', 'conversations']
            
        payload = {
            "interval": f"{offset_30days}/{to_date}",
            "segmentFilters": [
                {
                "type": "and",
                "predicates": [
                    {
                        "dimension": "purpose",
                        "value": "agent"
                    },
                    {
                        "dimension": "direction",
                        "value": "inbound"
                    },
                    {
                        "dimension": "segmentEnd",
                        "value": f"{from_date}/{to_date}"
                    }
                ]
                }
            ],
            "order": "asc",
            "paging": {
                "pageSize": 100,
                "pageNumber": 1
            }
        }
        
        start_time = time.time()
        
        response = requests.post(url, json=payload, headers=headers).json()
        time.sleep(0.1)
        
        pages = round(response['totalHits'] / 100)
        cur_page = 1

        payload['paging']['pageNumber'] = str(cur_page)
        print(f'Total: {pages}')
        
        while pages > 0 and cur_page <= pages:
            print(cur_page, sep='  ', end=' ', flush=True)
            try:
                self.authorize()
                headers['Authorization'] = f"Bearer {self.access_token}"
                
                response = requests.post(url, json=payload, headers=headers).json()
                df_metrics, depacked_df_list = self.depack_json(response['conversations'], columns_to_depack=metrics, lis_df=[])
                df_segments, _ = self.depack_json(response['conversations'], columns_to_depack=segments, lis_df=[])
                
                depacked_df_list.insert(0, df_metrics)
                depacked_df_list.insert(0, df_segments)

                for i in range(len(tables)):
                    # print(SQL_table.replace(report_type, names[i]))
                    # print(depacked_df_list[i])
                    SQLConnection.insert(depacked_df_list[i], SQL_table.replace('conversations', names[i]), self.API_domain, columns=ultra_dic['dict_columns'][names[i]])
                
                cur_page += 1
                payload['paging']['pageNumber'] = str(cur_page)
            except Exception as e:
                print(f'Error on page {cur_page}: {e}\n{pd.DataFrame(response)}')
                break

        elapsedTime = time.time() - start_time
        print(f'\nTotal Time to load Data Report: {elapsedTime} Sec')


    def load_evaluations(self):
        url_base = f'{self.base_API}/quality/evaluations/query'
        # SQL_Table = f'[{self.SQLschema}].[users_LOB]'

        # SQLConnection.truncate(SQL_Table, self.API_domain)

        self.authorize()
        
        headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {self.access_token}"
        }

        df_users = SQLConnection.select(self.API_domain, 'select id from Genesys.users')

        for i in range(df_users.shape[0]):
            userId = df_users['id'].iloc[i]
            url = f'{url_base}?agentUserId={userId}'

            response = requests.get(url, headers=headers).json()
            # print(url)
            # print(response)
            df_response = pd.DataFrame(response)

            if not df_response.empty:
                print(df_response)
            # else:
                # print(f'{userId} empty')


    def load_data(self, tables, temp, start_time=None, end_time=None, offset_minutes=1440, interval_minutes=1440):
            SQL_tables = []

            if start_time == None:
                end_time = datetime.utcnow() + timedelta(minutes=-1)
                if type(offset_minutes) == int:
                    start_time = end_time + timedelta(minutes=-offset_minutes)
            elif type(start_time) == str:
                start_time = datetime.fromisoformat(start_time)
                end_time = datetime.fromisoformat(end_time)

            if tables == 'All':
                report_types = self.report_types
            else:
                report_types = tables
            
            if temp:
                self.SQLschema = self.SQLschema + 'Temp'

            for table in report_types:
                SQL_tables.append(f'[{self.SQLschema}].[{table}]')

            for i in range(len(SQL_tables)):
                now = datetime.utcnow()
                
                if offset_minutes == 'max':
                    if report_types[i] == 'conversations':
                        query = 'select max(conversationStart) from V_Genesys_conversations_metrics'
                    elif report_types[i] == 'users_presence':
                        query = 'select max(endTime) from V_Genesys_presence'
                    start_time = SQLConnection.select(self.API_domain, query).iloc[0][0] + timedelta(hours=+7)
                
                aux_start_time = start_time
                aux_end_time = start_time + timedelta(minutes=interval_minutes)

                if aux_end_time > end_time:
                    aux_end_time = end_time

                if 'Temp' in SQL_tables[i]: 
                    SQLConnection.truncate(SQL_tables[i], self.API_domain)
                    
                    if report_types[i] == 'conversations':
                        SQLConnection.truncate(SQL_tables[i].replace('conversations', 'conversations_segments'), self.API_domain)
                        SQLConnection.truncate(SQL_tables[i].replace('conversations', 'conversations_metrics'), self.API_domain)
                        SQLConnection.truncate(SQL_tables[i].replace('conversations', 'conversations_participants'), self.API_domain)

                while aux_end_time <= end_time and aux_end_time <= now:
                    print(f'\n{SQL_tables[i]} {self.API_domain}')
                    print(f'Load until: {end_time}')
                    print(f'Loading {aux_start_time} -> {aux_end_time}')

                    from_date = aux_start_time.strftime('%Y-%m-%dT%H:%M:%S')
                    to_date = aux_end_time.strftime('%Y-%m-%dT%H:%M:%S')

                    if report_types[i] == 'users_presence':
                        self.load_usersPresence(SQL_tables[i], from_date, to_date, offset_minutes)
                    if report_types[i] == 'conversations':
                        self.load_conversations(SQL_tables[i], end_time, from_date, to_date, offset_minutes)

                    aux_start_time = aux_start_time + timedelta(minutes=interval_minutes)
                    aux_end_time = aux_start_time + timedelta(minutes=interval_minutes)

                    if (aux_end_time > end_time) and (aux_start_time < end_time):
                        aux_end_time = end_time
                    
            print('Finish loading Data\n')


