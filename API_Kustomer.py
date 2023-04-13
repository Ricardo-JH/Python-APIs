from datetime import datetime, timedelta
from API_parameters import kustomer_dic
from warnings import simplefilter
import SQLConnection
import pandas as pd
import requests
import time


simplefilter(action="ignore", category=pd.errors.PerformanceWarning)


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
                lis_df.insert(0, df_remain.fillna(''))
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
        
        return df_lv0.fillna(''), lis_df
    

    def load_users(self):
            url = f'{self.base_API}/users'
            next_url = f'{self.base_API}/users?pageSize=1000'
            SQL_Table = f'[{self.SQLschema}].[users]'
            last_page = False

            users = {
                'attributes': ['id'] 
            }

            SQLConnection.truncate(SQL_Table, self.API_domain)

            while not last_page:

                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
                }
                
                start_time = time.time()

                # print(url)
                print(next_url)
                response = requests.get(next_url, headers=headers).json()

                df_response, _ = self.depack_json(response['data'], columns_to_depack=users, lis_df=[])

                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)

                elapsedTime = time.time() - start_time
                print(f'Time to get Users Data: {elapsedTime} Sec')

                SQLConnection.insert(df_response, SQL_Table, self.API_domain, columns=kustomer_dic['dict_columns']['users'])
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/users', next_url)
                
            print('\nFinish Updating Users Data')


    def load_teams(self):
            url = f'{self.base_API}/teams'
            next_url = f'{self.base_API}/teams?pageSize=1000'
            SQL_Table = f'[{self.SQLschema}].[teams]'
            last_page = False

            users = {
                'attributes': ['id'],
                'attributes.members': ['id']
            }

            SQLConnection.truncate(SQL_Table, self.API_domain)
            SQLConnection.truncate(SQL_Table.replace('teams', 'team_members'), self.API_domain)

            start_time = time.time()

            while not last_page:

                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
                }
                
                print(next_url)
                response = requests.get(next_url, headers=headers).json()
                df_team_members, df_teams = self.depack_json(response['data'], columns_to_depack=users, lis_df=[])

                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)

                elapsedTime = time.time() - start_time
                print(f'Time to get Teams Data: {elapsedTime} Sec')

                SQLConnection.insert(df_team_members, SQL_Table.replace('teams', 'team_members'), self.API_domain)
                SQLConnection.insert(df_teams[0], SQL_Table, self.API_domain, columns=kustomer_dic['dict_columns']['teams'])
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/teams?pageSize=1000', next_url)
                
            print('\nFinish Updating Teams Data')
            print(f'Elapsed Time: {time.time() - start_time} Sec')


    def load_queues(self):
            url = f'{self.base_API}/routing/queues'
            next_url = f'{self.base_API}/routing/queues?pageSize=1000'
            SQL_Table = f'[{self.SQLschema}].[queues]'
            last_page = False

            users = {
                'attributes': ['id']
            }

            SQLConnection.truncate(SQL_Table, self.API_domain)

            start_time = time.time()

            while not last_page:

                headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
                }
                
                print(next_url)
                response = requests.get(next_url, headers=headers).json()
                df_queues, _ = self.depack_json(response['data'], columns_to_depack=users, lis_df=[])
                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)

                elapsedTime = time.time() - start_time
                print(f'Time to get Queues Data: {elapsedTime} Sec')

                SQLConnection.insert(df_queues, SQL_Table, self.API_domain, columns=kustomer_dic['dict_columns']['queues'])
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/routing/queues?pageSize=1000', next_url)
                
            print('\nFinish Updating Queues Data')
            print(f'Elapsed Time: {time.time() - start_time} Sec')

   
    def load_sms_note(self, report_type, SQL_table, from_date, to_date, offset_minutes):
            url = f'{self.search_API}'
            next_url = f'{self.search_API}?pageSize=500&page=1'
            last_page = False

            attributes = {
                'attributes': ['id'],
                'attributes.channels': '',
                'attributes.assistant.assistantId': '',
                'attributes.firstDone.assignedUsers': '',
                'relationships.conversation': '',
                'relationships.conversation.data': ''
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
            }
            
            payload = {
                "and": [
                    { f"{report_type}_updated_at": { "gte": f"{from_date}" } },
                    { f"{report_type}_updated_at": { "lte": f"{to_date}" } }
                ],
                "queryContext": f"{report_type}",
                # "timeZone": "America/Tijuana",
                "or":[]
            }

            if offset_minutes == 'max':
                payload['and'].pop(1)

            print('Total:', requests.post(next_url, headers=headers, json=payload).json()['meta']['totalPages'])
            start_time = time.time()

            while not last_page:
                cur_page = next_url[-2:].replace('=', '')
                print(cur_page, sep='  ', end=' ', flush=True)
                
                response = requests.post(next_url, headers=headers, json=payload).json()
                
                try:
                    df_response, _ = self.depack_json(response['data'], columns_to_depack=attributes, lis_df=[])
                    SQLConnection.insert(df_response, SQL_table, self.API_domain, columns=kustomer_dic['dict_columns'][report_type])
                except KeyError as KeyErr:
                    print(f'Error on page {cur_page}. {KeyErr}')
                except ValueError as ValErr:
                    print(f'Error on data page {cur_page}. {ValErr}')

                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/customers/search', next_url)
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get Data: {elapsedTime} Sec')
            
            print(f'\nFinish Updating {report_type}')


    def load_conversation(self, SQL_table, from_date, to_date, offset_minutes):
            url = f'{self.search_API}'
            next_url = f'{self.search_API}?pageSize=500&page=1'
            last_page = False

            conversation_attributes = {
                'attributes': ['id'],
                'attributes.channels': ['id'],
                'attributes.assistant.assistantId': '',
                'attributes.firstDone.assignedUsers': '',
                'relationships.conversation': '',
                'relationships.conversation.data': ''
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
            }
            
            payload = {
                "and": [
                    { "conversation_updated_at": { "gte": f"{from_date}" } }, # created / updated
                    { "conversation_updated_at": { "lte": f"{to_date}" } }
                ],
                "queryContext": "conversation",
                # "timeZone": "America/Tijuana",
                "or":[]
            }

            if offset_minutes == 'max':
                payload['and'].pop(1)

            print('Total:', requests.post(next_url, headers=headers, json=payload).json()['meta']['totalPages'])
            start_time = time.time()

            while not last_page:
                cur_page = next_url[-2:].replace('=', '')
                print(cur_page, sep='  ', end=' ', flush=True)
                
                response = requests.post(next_url, headers=headers, json=payload).json()
                
                try:
                    df_channels, df_response = self.depack_json(response['data'], columns_to_depack=conversation_attributes, lis_df=[])
                    
                    if df_response:
                        df_response, _ = self.depack_json(df_response[0], columns_to_depack=conversation_attributes, lis_df=[])
                    else:
                        df_response = df_channels.loc[:, df_channels.columns!='attributes.channels']
                        df_channels = df_channels[['id', 'attributes.channels']]

                    SQLConnection.insert(df_channels, SQL_table.replace('conversation', 'conversation_channels'), self.API_domain)
                    SQLConnection.insert(df_response, SQL_table, self.API_domain, columns=kustomer_dic['dict_columns']['conversation'])
                except KeyError as KeyErr:
                    print(f'Error on page {cur_page}. {KeyErr}')
                except ValueError as ValErr:
                    print(f'Error on data page {cur_page}. {ValErr}')

                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/customers/search', next_url)
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get Data: {elapsedTime} Sec')
            
            print(f'\nFinish Updating conversation')


    def load_conversation_time(self, SQL_table, from_date, to_date, offset_minutes):
            url = f'{self.search_API}'
            next_url = f'{self.search_API}?pageSize=500&page=1'
            last_page = False

            conversation_attributes = {
                'attributes': ['id'],
                'attributes.channels': ['id'],
                'attributes.assignedUsers': ''
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
            }
            
            payload = {
                "and": [
                    { "conversation_time_handle_at": { "gte": f"{from_date}" } },
                    { "conversation_time_handle_at": { "lte": f"{to_date}" } }
                ],
                "queryContext": "conversation_time",
                # "timeZone": "America/Tijuana",
                "or":[]
            }

            if offset_minutes == 'max':
                payload['and'].pop(1)

            print('Total:', requests.post(next_url, headers=headers, json=payload).json()['meta']['totalPages'])
            start_time = time.time()

            while not last_page:
                cur_page = next_url[-2:].replace('=', '')
                print(cur_page, sep='  ', end=' ', flush=True)
                
                response = requests.post(next_url, headers=headers, json=payload).json()
                
                try:
                    df_channels, df_response = self.depack_json(response['data'], columns_to_depack=conversation_attributes, lis_df=[])

                    if df_response:
                        df_response, _ = self.depack_json(df_response[0], columns_to_depack=conversation_attributes, lis_df=[])
                    else:
                        df_response = df_channels.loc[:, df_channels.columns!='attributes.channels']
                        df_channels = df_channels[['id', 'attributes.channels']]
                    
                    SQLConnection.insert(df_channels, SQL_table.replace('conversation_time', 'conversation_time_channels'), self.API_domain)
                    SQLConnection.insert(df_response, SQL_table, self.API_domain, columns=kustomer_dic['dict_columns']['conversation_time'])
                except KeyError as KeyErr:
                    print(f'Error on page {cur_page}. {KeyErr}')
                except ValueError as ValErr:
                    print(f'Error on data page {cur_page}. {ValErr}')
                
                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/customers/search', next_url)
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get Data: {elapsedTime} Sec')
            
            print(f'\nFinish Updating conversation_time')


    def load_work_item(self, SQL_table, from_date, to_date, offset_minutes):
            url = f'{self.search_API}'
            next_url = f'{self.search_API}?pageSize=500&page=1'
            last_page = False

            conversation_attributes = {
                'attributes': ['id'],
                'attributes.ivr': '',
                'attributes.handle': '',
                'attributes.wrapUp': '',
                'attributes.abandoned': '',
                'attributes.lastRevision': '',
                'attributes.resource': '',
                'attributes.resource.sla': ''
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
            }
            
            payload = {
                "and": [
                    { "work_item_handle_completed_at": { "gte": f"{from_date}" } },
                    { "work_item_handle_completed_at": { "lte": f"{to_date}" } }
                ],
                "queryContext": "work_item",
                # "timeZone": "America/Tijuana",
                "or":[]
            }

            if offset_minutes == 'max':
                payload['and'].pop(1)

            print('Total:', requests.post(next_url, headers=headers, json=payload).json()['meta']['totalPages'])
            start_time = time.time()

            while not last_page:
                cur_page = next_url[-2:].replace('=', '')
                print(cur_page, sep='  ', end=' ', flush=True)
                
                response = requests.post(next_url, headers=headers, json=payload).json()
                
                try:
                    df_response, _ = self.depack_json(response['data'], columns_to_depack=conversation_attributes, lis_df=[])
                    
                    SQLConnection.insert(df_response, SQL_table, self.API_domain, columns=kustomer_dic['dict_columns']['work_item'])
                except KeyError as KeyErr:
                    print(f'Error on page {cur_page}. {KeyErr}')
                except ValueError as ValErr:
                    print(f'Error on data page {cur_page}. {ValErr}')
                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/customers/search', next_url)
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get Data: {elapsedTime} Sec')
            
            print(f'\nFinish Updating work_item')


    def load_work_session(self, SQL_table, from_date, to_date, offset_minutes):
            url = f'{self.search_API}'
            next_url = f'{self.search_API}?pageSize=500&page=1'
            last_page = False

            conversation_attributes = {
                'attributes': ['id'],
                'attributes.totalUnavailable': '',
                'attributes.totalUnavailableIdleCapacity': '',
                'attributes.abandoned': '',
                'attributes.lastRevision': '',
                'attributes.resource': '',
                'attributes.resource.sla': '',
                'relationships.queues': '',
                'relationships.queues.data': ''
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.API_key}"
            }
            
            payload = {
                "and": [
                    { "work_session_updated_at": { "gte": f"{from_date}" } },
                    { "work_session_updated_at": { "lte": f"{to_date}" } }
                ],
                "queryContext": "work_session",
                # "timeZone": "America/Tijuana",
                "or":[]
            }

            if offset_minutes == 'max':
                payload['and'].pop(1)

            print('Total:', requests.post(next_url, headers=headers, json=payload).json()['meta']['totalPages'])
            start_time = time.time()

            while not last_page:
                cur_page = next_url[-2:].replace('=', '')
                print(cur_page, sep='  ', end=' ', flush=True)
                
                response = requests.post(next_url, headers=headers, json=payload).json()
                
                try:
                    df_response, _ = self.depack_json(response['data'], columns_to_depack=conversation_attributes, lis_df=[])
                    SQLConnection.insert(df_response, SQL_table, self.API_domain, columns=kustomer_dic['dict_columns']['work_session'])
                except KeyError as KeyErr:
                    print(f'Error on page {cur_page}. {KeyErr}')
                except ValueError as ValErr:
                    print(f'Error on data page {cur_page}. {ValErr}')
                try:
                    next_url = response['links']['next']
                except KeyError as KeyErr:
                    next_url = None
                    time.sleep(0.5)
                
                if next_url == None:
                    last_page = True
                else:
                    next_url = url.replace('/v1/customers/search', next_url)
            
            elapsedTime = time.time() - start_time
            print(f'\nTime to get Data: {elapsedTime} Sec')
            
            print(f'\nFinish Updating work_session')


    def load_data(self, tables, temp, start_time=None, end_time=None, offset_minutes=24*60, interval_minutes=24*60):
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
                    reference_column = kustomer_dic['reference_maxDate'][i]
                    table =SQL_tables[i].replace('Temp', '')
                    query = f'select Top 1 max([attributes.{reference_column}]) max_updatedAt from {table}'
                    start_time = SQLConnection.select(self.API_domain, query).iloc[0][0] + timedelta()

                aux_start_time = start_time
                aux_end_time = start_time + timedelta(minutes=interval_minutes)

                if aux_end_time > end_time:
                    aux_end_time = end_time

                if 'Temp' in SQL_tables[i]: 
                    SQLConnection.truncate(SQL_tables[i], self.API_domain)

                    if report_types[i] == 'conversation':
                        SQLConnection.truncate(SQL_tables[i].replace('conversation', 'conversation_channels'), self.API_domain)
                    if report_types	[i] == 'conversation_time':
                        SQLConnection.truncate(SQL_tables[i].replace('conversation_time', 'conversation_time_channels'), self.API_domain)

                while aux_end_time <= end_time and aux_end_time <= now:
                    
                    print(f'\n{SQL_tables[i]} {self.API_domain}')
                    print(f'Load until: {end_time}')
                    print(f'Loading {aux_start_time} -> {aux_end_time}')

                    from_date = aux_start_time.strftime('%Y-%m-%dT%H:%M:%S')
                    to_date = aux_end_time.strftime('%Y-%m-%dT%H:%M:%S')
                    
                    if report_types[i] in ['note', 'message']:
                        self.load_sms_note(report_types[i], SQL_tables[i], from_date=from_date, to_date=to_date, offset_minutes=offset_minutes)
                    elif report_types[i] == 'conversation':
                        self.load_conversation(SQL_tables[i], from_date=from_date, to_date=to_date, offset_minutes=offset_minutes)
                    elif report_types[i] == 'conversation_time':
                        self.load_conversation_time(SQL_tables[i], from_date=from_date, to_date=to_date, offset_minutes=offset_minutes)
                    elif report_types[i] == 'work_item':
                        self.load_work_item(SQL_tables[i], from_date=from_date, to_date=to_date, offset_minutes=offset_minutes)
                    elif report_types[i] == 'work_session':
                        self.load_work_session(SQL_tables[i], from_date=from_date, to_date=to_date, offset_minutes=offset_minutes)
                    
                    aux_start_time = aux_start_time + timedelta(minutes=interval_minutes)
                    aux_end_time = aux_start_time + timedelta(minutes=interval_minutes)

                    if (aux_end_time > end_time) and (aux_start_time < end_time):
                        aux_end_time = end_time
                    
            print('Finish loading Data\n')

