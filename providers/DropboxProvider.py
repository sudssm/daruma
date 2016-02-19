import dropbox
import urllib3
from contextlib import contextmanager
from custom_exceptions import exceptions
from BaseProvider import BaseProvider

# From Dropbox developer site. 
DBOX_APP_KEY = "btmom5enals52c3"
DBOX_APP_SECRET = "dl9yxq1331z9z81"


class DropboxProvider(BaseProvider):
    def __init__(self, access_token):
        """
        Initialize a dropbox provider.

        Args:
            access_token: the access_token for the user. 
        """
        
        self.access_token = access_token
        self.client = dropbox.client.DropboxClient(self.access_token)

    @staticmethod
    def new_connection():
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY,DBOX_APP_SECRET)
        authorize_url = flow.start()
        return authorize_url

    @staticmethod
    def finish_connection(authorization_code):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY,DBOX_APP_SECRET)
        try:
            access_token,_ = flow.finish(authorization_code)
            client = dropbox.client.DropboxClient(access_token)
            return DropboxProvider(access_token=access_token)
        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(self)
        except dropbox.oauth.NotApprovedException:
            raise exceptions.AuthFailure(self)
        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(self)
        except Exception:
            raise exceptions.LibraryException


    @contextmanager
    def exception_handler(self):
        try:
            yield
        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(self)
        except dropbox.rest.ErrorResponse as e:
            if e.status == 401:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)
        except Exception:
            raise exceptions.LibraryException


    def connect(self):
        with self.exception_handler():
            account_info = self.client.account_info()
        

    def get(self, filename):
        with self.exception_handler():
            f, metadata = self.client.get_file_and_metadata(filename)
            return f.read()
        

    def put(self, filename, data):
        with self.exception_handler():
            response = self.client.put_file(filename, data, overwrite=True)
        

    def delete(self, filename):
        with self.exception_handler():
            self.client.file_delete(filename)
        

    def wipe (self):
        with self.exception_handler():
            entries = self.client.delta()['entries']
            for e in entries:
                self.client.file_delete(e[0])
        




