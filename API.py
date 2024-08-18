from API_Kustomer import API_Kustomer
from API_Genesys import API_Genesys
from API_Talkdesk import API_Talkdesk


class API:
    def __init__(self, API_domain):
        self.API_domain = API_domain
        self.API = None
        self.set_API()


    def set_API(self):
        if self.API_domain in ['therabody', 'rootinsurance']:
            self.API = API_Talkdesk(self.API_domain)
        elif self.API_domain == 'ultra':
            self.API = API_Genesys(self.API_domain)
        elif self.API_domain == 'kustomer':
            self.API = API_Kustomer(self.API_domain)
