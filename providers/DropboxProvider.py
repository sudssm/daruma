import dropbox

import urllib3
from contextlib import contextmanager
from custom_exceptions import exceptions
from BaseProvider import BaseProvider

# TODO use a manager
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
    @contextmanager
    def exception_handler(provider):
        try:
            yield
        except dropbox.oauth.NotApprovedException:
            raise exceptions.AuthFailure(provider)
        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(provider)
        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(provider)
        except dropbox.rest.ErrorResponse as e:
            if e.status in [401,400]:
                raise exceptions.AuthFailure(provider)
            raise exceptions.ProviderOperationFailure(provider)
        except Exception:
            raise exceptions.LibraryException


    @staticmethod
    def new_connection():
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY, DBOX_APP_SECRET)
        authorize_url = flow.start()
        return authorize_url


    @staticmethod
    def finish_connection(authorization_code):
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY, DBOX_APP_SECRET)
        with DropboxProvider.exception_handler(None):
            access_token,_ = flow.finish(authorization_code)
            # TODO credential management
            return DropboxProvider(access_token=access_token)
        

    def connect(self):
        with DropboxProvider.exception_handler(self):
            self.client.account_info()

    def get(self, filename):
        with DropboxProvider.exception_handler(self):
            f, metadata = self.client.get_file_and_metadata(filename)
            return f.read()

    def put(self, filename, data):
        with DropboxProvider.exception_handler(self):
            self.client.put_file(filename, data, overwrite=True)


    def delete(self, filename):
        with DropboxProvider.exception_handler(self):
            self.client.file_delete(filename)

    def wipe(self):
        with DropboxProvider.exception_handler(self):
            entries = self.client.delta()['entries']
            for e in entries:
                self.client.file_delete(e[0])
