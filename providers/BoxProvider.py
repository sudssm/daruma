from tools.utils import parse_url
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.OAuthProvider import OAuthProvider
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxOAuthException, BoxAPIException
from StringIO import StringIO
from requests.exceptions import ReadTimeout
import json


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
        self.access_token, self.refresh_token = None, None
        self.write_tokens = True

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
        finally:
            self._persist_tokens()

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
        if self.write_tokens and self.access_token is not None:
            user_credentials = {"access_token": self.access_token, "refresh_token": self.refresh_token}
            self.credential_manager.set_user_credentials(self.__class__, self.uid, user_credentials)
        self.write_tokens = False

    def _connect(self, user_credentials):
        def store_tokens_callback(access_token, refresh_token):
            self.write_tokens = True
            self.access_token = access_token
            self.refresh_token = refresh_token

        def load_email():
            with self.exception_handler():
                self._email = self.client.user(user_id='me').get()['login']

        def make_app_folder():
            with self.exception_handler():
                box_root_folder = self.client.folder(self.BOX_ROOT_ID)

                try:  # make an app-specific folder if one does not already exist
                    _, folder_id, _ = box_root_folder.create_subfolder(self.ROOT_DIR)
                except BoxAPIException as e:
                    folder_id = e.context_info['conflicts'][0]['id']

                self.app_folder = self.client.folder(folder_id)

        def prime_cache():
            with self.exception_handler():
                # get all items
                files = []
                offset = 0
                while len(files) == offset:
                    files += self.app_folder.get_items(self.MAX_BOX_LIMIT, offset=offset)
                    offset += self.MAX_BOX_LIMIT
                self.id_cache = {user_file.name: user_file.object_id for user_file in files}

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

        load_email()
        make_app_folder()
        prime_cache()

    @property
    def uid(self):
        return self._email

    def get(self, filename):
        with self.exception_handler():
            box_file = self.client.file(self.id_cache[filename])
            return box_file.content()

    def put(self, filename, data):
        data_stream = StringIO(data)

        with self.exception_handler():
            if filename in self.id_cache:
                existing_file = self.client.file(self.id_cache[filename])
                existing_file.update_contents_with_stream(data_stream)
            else:
                new_file = self.app_folder.upload_stream(data_stream, filename)
                self.id_cache[filename] = new_file.object_id

    def delete(self, filename):
        with self.exception_handler():
            box_file = self.client.file(self.id_cache[filename])
            box_file.delete()
            self.id_cache.pop(filename, None)

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
