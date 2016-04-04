import dropbox
import urllib3
from urlparse import urlparse, parse_qs
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider
from providers.CredentialManager import CredentialManager


class DropboxProvider(BaseProvider):
    @staticmethod
    def load(credential_manager):
        """
        Attempts to load all DropboxProviders that have user credential stored
        Returns a list of valid DropboxProviders
        """
        credentials = credential_manager.get_user_credentials(DropboxProvider.__module__)
        db_providers = []
        for auth_token in credentials:
            db_provider = DropboxProvider(credential_manager)
            try:
                db_provider._connect(auth_token)
                db_providers.append(db_provider)
            except:
                continue
        return db_providers

    def __init__(self, credential_manager):
        """
        Initialize a dropbox provider.
        Not functional until start_connection and finish_connection are called.
        Args: credential_manager, a credential_manager with information about DropboxProviders
        """
        super(DropboxProvider, self).__init__()
        self.credential_manager = credential_manager

    @contextmanager
    def exception_handler(self):
        try:
            yield

        except (dropbox.oauth.NotApprovedException, dropbox.oauth.BadStateException,
                dropbox.oauth.CsrfException, dropbox.oauth.BadRequestException):
            raise exceptions.AuthFailure(self)

        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(self)

        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(self)

        except dropbox.rest.ErrorResponse as e:
            if e.status in [401, 400]:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)

        except Exception:
            raise exceptions.LibraryException

    def start_connection(self):
        """
        Initiate a new connection to Dropbox.
        Args: app_key, app_secret - app identifiers, provided by Dropbox
        Returns: a url that allows the user to log in
        Raises: IOError if there was a problem reading app credentials
                ProviderOperationFailure if there was a problem starting flow
        """
        try:
            credentials = self.credential_manager.get_app_credentials(DropboxProvider.__module__)
            app_key, app_secret = credentials["app_key"], credentials["app_secret"]
        except (AttributeError, ValueError):
            raise IOError("No valid app credentials found!")

        with self.exception_handler():
            self.flow = dropbox.client.DropboxOAuth2Flow(app_key, app_secret, "http://localhost", {}, "dropbox-auth-csrf-token")
            authorize_url = self.flow.start()

        return authorize_url

    def finish_connection(self, url):
        """
        Finalize the connection to Dropbox
        Args: url - a localhost url, resulting from a redirect after start_connection
        """
        # parse url
        params = parse_qs(urlparse(url).query)
        params = {k: v[0] for k, v in params.items()}

        # get auth_token
        with self.exception_handler():
            auth_token, _, _ = self.flow.finish(params)

        self._connect(auth_token)

    def _connect(self, auth_token):
        with self.exception_handler():
            self.client = dropbox.client.DropboxClient(auth_token)
            self.user_id = self.client.account_info()['uid']
        self.credential_manager.set_user_credentials(DropboxProvider.__module__, self.user_id, auth_token)

    def get(self, filename):
        with self.exception_handler():
            with client.get_file(filename) as f:
                return f.read()

    def put(self, filename, data):
        with self.exception_handler():
            self.client.put_file(filename, data, overwrite=True)

    def delete(self, filename):
        with self.exception_handler():
            self.client.file_delete(filename)

    def wipe(self):
        with self.exception_handler():
            has_more = True
            while has_more:
                delta = self.client.delta()
                has_more = delta['has_more']
                entries = delta['entries']
                for e in entries:
                    self.delete(e[0])
