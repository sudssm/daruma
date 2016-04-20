from tools.utils import parse_url
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.OAuthProvider import OAuthProvider
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxOAuthException, BoxAPIException
from StringIO import StringIO
from requests.exceptions import ReadTimeout
import json

def try_with_refresh(func):
    """
    Runs func. If func raises an AuthFailure, refreshes tokens and tries again.
    Updates self.auth_token and self.refresh_token
    Write updated credentials to the internal credential_manager after running func
    """
    def refresh_wrapper(*args, **kwargs):
        self = args[0]     
        try:
            return func(*args, **kwargs)
        except exceptions.AuthFailure:
            with self.exception_handler():
                # self.auth_token and self.refresh_token are updated in store_tokens_callback
                self.client.auth.refresh(self.access_token)
            result = func(*args, **kwargs)
            self._persist_tokens()
            return result
    return refresh_wrapper

class BoxProvider(OAuthProvider):
    BOX_ROOT_ID = '0'  # The root of the Box system (per Box docs)
    MAX_BOX_LIMIT = 1000  # the maximum number of items returned from a Box request

    @classmethod
    def provider_identifier(cls):
        return "box"

    @classmethod
    def provider_name(cls):
        return "Box"

    def __init__(self, credential_manager):
        super(BoxProvider, self).__init__(credential_manager)
        self.id_cache, self._email, self._app_credentials = None, None, None

    @property
    def app_credentials(self):
        """
        A dictionary with keys 'client_id' and client_secret'
        """
        if self._app_credentials is None:
            try:
                self._app_credentials = self.credential_manager.get_app_credentials(self.__class__)
            except (KeyError, TypeError):
                raise IOError("No valid app credentials found!")
        return self._app_credentials

    @contextmanager
    def exception_handler(self):
        try:
            yield
        except BoxOAuthException:
            raise exceptions.AuthFailure(self)
        except BoxAPIException:
            raise exceptions.ProviderOperationFailure(self)
        except ReadTimeout:
            raise exceptions.ConnectionFailure(self)
        except Exception:
            raise exceptions.ProviderOperationFailure(self)

    def start_connection(self):
        self.oauth = OAuth2(client_id=self.app_credentials["client_id"], client_secret=self.app_credentials["client_secret"])
        with self.exception_handler():
            authorize_url, self.csrf_token = self.oauth.get_authorization_url(self.get_oauth_redirect_url())

        return authorize_url

    def finish_connection(self, url):
        params = parse_url(url)

        try:  # get auth_token
            auth_token = params["code"]
            assert self.csrf_token == params["state"]
        except AssertionError:  # csrf mismatch or csrf not found
            raise exceptions.AuthFailure(self)
        except KeyError:
            try:
                error_code = params["error"]
            except KeyError:
                raise exceptions.ProviderOperationFailure(self)
            if error_code == "invalid_request" or error_code == "unsupported_response_type":
                raise exceptions.ProviderOperationFailure(self)
            elif error_code == "access_denied" or error_code == "server_error":
                raise exceptions.AuthFailure(self)
            elif error_code == "temporarily_unavailable":
                raise exceptions.ConnectionFailure(self)
            else:
                raise exceptions.ProviderOperationFailure(self)

        credentials = {}
        with self.exception_handler():
            credentials["access_token"], credentials["refresh_token"] = self.oauth.authenticate(auth_token)

        self._connect(credentials)

    def _persist_tokens(self):
        user_credentials = {"access_token": self.access_token, "refresh_token": self.refresh_token}
        self.credential_manager.set_user_credentials(self.__class__, self.uid, user_credentials)

    @try_with_refresh
    def load_email(self):
        with self.exception_handler():
            self._email = self.client.user(user_id='me').get()['login']

    @try_with_refresh
    def make_app_folder(self):
        with self.exception_handler():
            box_root_folder = self.client.folder(self.BOX_ROOT_ID)

            try:  # make an app-specific folder if one does not already exist
                _, folder_id, _ = box_root_folder.create_subfolder(self.ROOT_DIR)
            except BoxAPIException as e:
                folder_id = e.context_info['conflicts'][0]['id']

            self.app_folder = self.client.folder(folder_id)

    @try_with_refresh
    def prime_cache(self):
        with self.exception_handler():
            # get all items
            files = []
            offset = 0
            while len(files) == offset:
                files += self.app_folder.get_items(self.MAX_BOX_LIMIT, offset=offset)
                offset += self.MAX_BOX_LIMIT
            self.id_cache = {user_file.name: user_file.object_id for user_file in files}

    def _connect(self, user_credentials):
        def store_tokens_callback(access_token, refresh_token):
            self.access_token = access_token
            self.refresh_token = refresh_token

        # if this came from cache, it is a json string that needs to be converted
        if type(user_credentials) in [unicode, str]:
            user_credentials = json.loads(user_credentials)

        self.access_token, self.refresh_token = user_credentials["access_token"], user_credentials["refresh_token"]

        oauth = OAuth2(client_id=self.app_credentials["client_id"],
                       client_secret=self.app_credentials["client_secret"],
                       store_tokens=store_tokens_callback,
                       access_token=self.access_token,
                       refresh_token=self.refresh_token)

        self.client = Client(oauth)

        self.load_email()
        self.make_app_folder()
        self.prime_cache()

        self._persist_tokens()

    @property
    def uid(self):
        return self._email

    @try_with_refresh
    def get(self, filename):
        with self.exception_handler():
            box_file = self.client.file(self.id_cache[filename])
            return box_file.content()

    @try_with_refresh
    def put(self, filename, data):
        data_stream = StringIO(data)

        with self.exception_handler():
            if filename in self.id_cache:
                existing_file = self.client.file(self.id_cache[filename])
                existing_file.update_contents_with_stream(data_stream)
            else:
                new_file = self.app_folder.upload_stream(data_stream, filename)
                self.id_cache[filename] = new_file.object_id

    @try_with_refresh
    def delete(self, filename):
        with self.exception_handler():
            box_file = self.client.file(self.id_cache[filename])
            box_file.delete()
            self.id_cache.pop(filename, None)

    @try_with_refresh
    def wipe(self):
        with self.exception_handler():
            try:
                for _, file_id in self.id_cache.items():
                    box_file = self.client.file(file_id)
                    box_file.delete()
            except:
                raise
            finally:
                self.id_cache = {}

