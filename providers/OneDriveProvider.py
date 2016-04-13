import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from contextlib import contextmanager


REDIRECT_URL = "http://localhost:8080/"
CLIENT_SECRET = "M1d6B39lFRDg4Wboicv6DgVhwjG-Ge1x"
CLIENT_ID = "000000004417E11D"

class OneDriveProvider(BaseProvider):
    
    def __init__(self):
        client = onedrivesdk.get_default_client(client_id=CLIENT_ID,
                                            	scopes=['wl.signin',
                                                    	'wl.offline_access',
                                                    	'onedrive.appfolder'])
        auth_url = client.auth_provider.get_auth_url(REDIRECT_URL)

        # code = GetAuthCodeServer.get_auth_code(auth_url, REDIRECT_URL)
        client.auth_provider.authenticate(code, REDIRECT_URL, CLIENT_SECRET)




    @staticmethod
    def get_credentials():
    	pass

    @staticmethod
    @contextmanager
    def exception_handler(provider):
    	pass
       
    def connect(self):
    	pass
        

    def _get_id(self, filename):
        pass


    def get(self, filename):
    	pass

    def put(self, filename, data):
        pass


    def delete(self, filename):
        pass


    def wipe (self):
        pass

