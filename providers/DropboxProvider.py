import dropbox

import urllib3
from urlparse import urlparse, parse_qs
from contextlib import contextmanager
from custom_exceptions import exceptions
from BaseProvider import BaseProvider
from CredentialManager import CredentialManager

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
        self.dropbox = dropbox.Dropbox(self.access_token)
        super(DropboxProvider, self).__init__()

    @staticmethod
    @contextmanager
    def exception_handler(provider):
        try:
            yield
        # authentication exception
        except dropbox.oauth.NotApprovedException:
            raise exceptions.AuthFailure(provider)
        except dropbox.oauth.BadStateException:
            raise exceptions.AuthFailure(provider)
        except dropbox.oauth.CsrfException:
            raise exceptions.AuthFailure(provider)
        except dropbox.oauth.BadRequestException:
            raise exceptions.AuthFailure(provider)
        # operation exception
        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(provider)
        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(provider)
        except dropbox.rest.ErrorResponse as e:
            if e.status in [401, 400]:
                raise exceptions.AuthFailure(provider)
            raise exceptions.ProviderOperationFailure(provider)
        # except Exception:
        #     raise exceptions.LibraryException

    @staticmethod
    def new_connection_redirect(port):
        flow = dropbox.client.DropboxOAuth2Flow(DBOX_APP_KEY, DBOX_APP_SECRET, "http://localhost:%s" % str(port), {}, "dropbox-auth-csrf-token")
        authorize_url = flow.start()
        return authorize_url, flow

    @staticmethod
    def finish_connection_redirect(url, flow):
        # parse url
        params = parse_qs(urlparse(url).query)
        params = dict([(k, v[0]) for (k, v) in params.items()])

        # get access_token
        with DropboxProvider.exception_handler(None):
            access_token, _, _ = flow.finish(params)

            # store access_token
            CredentialManager.update_credentials(DropboxProvider, access_token)

    @staticmethod
    def new_connection():
        flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY, DBOX_APP_SECRET)
        authorize_url = flow.start()
        return authorize_url

    @staticmethod
    def finish_connection(authorization_code):
        flow = dropbox.client.DropboxOAuth2Flow(DBOX_APP_KEY, DBOX_APP_SECRET)
        with DropboxProvider.exception_handler(None):
            access_token, _ = flow.finish(authorization_code)
            CredentialManager.update_credentials(DropboxProvider, access_token)

            return DropboxProvider(access_token=access_token)

    def connect(self):
        with DropboxProvider.exception_handler(self):
            self.client.account_info()

    def get(self, filename):
        with DropboxProvider.exception_handler(self):
            f,_ = self.client.get_file_and_metadata(filename)
            return f.read()

    def put(self, filename, data):
        with DropboxProvider.exception_handler(self):
            self.client.put_file(filename, data, overwrite=True)


    def delete(self, filename):
        with DropboxProvider.exception_handler(self):
            self.client.file_delete(filename)

    def get_capacity(self):
        space_usage = self.dropbox.users_get_space_usage()
        used_space = space_usage.used
        total_allocated_space = space_usage.allocation.get_individual().allocated

        return used_space, total_allocated_space

    def wipe(self):
        with DropboxProvider.exception_handler(self):
            entries = self.client.delta()['entries']
            for e in entries:
                self.client.file_delete(e[0])
