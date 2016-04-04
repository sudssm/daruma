import dropbox

import urllib3
from urlparse import urlparse, parse_qs
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider
from providers.CredentialManager import CredentialManager


class DropboxProvider(BaseProvider):
    def __init__(self, access_token):
        """
        Initialize a dropbox provider.

        Args:
            access_token: the access_token for the user.
        """

        self.access_token = access_token
        self.client = dropbox.client.DropboxClient(self.access_token)
        super(DropboxProvider, self).__init__()

    @staticmethod
    @contextmanager
    def exception_handler(provider):
        try:
            yield

        except (dropbox.oauth.NotApprovedException, dropbox.oauth.BadStateException,
                dropbox.oauth.CsrfException, dropbox.oauth.BadRequestException):
            raise exceptions.AuthFailure(provider)

        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(provider)

        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(provider)

        except dropbox.rest.ErrorResponse as e:
            if e.status in [401, 400]:
                raise exceptions.AuthFailure(provider)
            raise exceptions.ProviderOperationFailure(provider)

        except Exception:
            raise exceptions.LibraryException

    @staticmethod
    def new_connection(app_key, app_secret):
        """
        Initiate a new connection to Dropbox.
        Args: app_key, app_secret - app identifiers, provided by Dropbox
        Returns: a url that begins the OAuth flow, and a flow object to be used with finish_connection
        """
        flow = dropbox.client.DropboxOAuth2Flow(app_key, app_secret, "http://localhost", {}, "dropbox-auth-csrf-token")
        authorize_url = flow.start()
        return authorize_url, flow

    @staticmethod
    def finish_connection(url, flow):
        """
        Finalize the connection to Dropbox
        Args: url - a localhost url, resulting from a redirect after new_connection
              flow - the flow object returned from new_connection
        Returns: a valid Dropbox access token
        """
        # parse url
        params = parse_qs(urlparse(url).query)
        params = {k: v[0] for k, v in params.items()}

        # get access_token
        with DropboxProvider.exception_handler(None):
            access_token, _, _ = flow.finish(params)

        return access_token

    def connect(self):
        with DropboxProvider.exception_handler(self):
            self.client.account_info()

    def get(self, filename):
        with DropboxProvider.exception_handler(self):
            f, _ = self.client.get_file_and_metadata(filename)
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
