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
    BOX_ROOT_ID = '0'
    MAX_BOX_LIMIT = 1000

    @classmethod
    def provider_identifier(cls):
        return "box"

    @classmethod
    def provider_name(cls):
        return "Box"

    def __init__(self, credential_manager):
        """
        Initialize a box provider.
        Not functional until start_connection and finish_connection are called.
        Args: credential_manager, a credential_manager with information about BoxProviders
        """
        super(BoxProvider, self).__init__(credential_manager)
        self.id_cache = {}

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

    def refresh_exception_handler(self, func):
        try:
            with self.exception_handler():
                return func()
        except exceptions.AuthFailure:
            with self.exception_handler():
                self.client.auth.refresh(self.access_token)
                return func()

    def _get_app_credentials(self):
        try:
            return self.client_id, self.client_secret
        except AttributeError:  # these attributes have not yet been set
            try:
                credentials = self.credential_manager.get_app_credentials(self.__class__)
                return credentials["client_id"], credentials["client_secret"]
            except (KeyError, TypeError):
                raise IOError("No valid app credentials found!")

    def start_connection(self):
        self.client_id, self.client_secret = self._get_app_credentials()

        self.oauth = OAuth2(client_id=self.client_id, client_secret=self.client_secret)
        with self.exception_handler():
            authorize_url, self.csrf_token = self.oauth.get_authorization_url('http://localhost')

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

    def _store_user_tokens(self, access_token, refresh_token):
        try:
            self.uid
        except AttributeError:
            with self.exception_handler():
                self.email = self.client.user(user_id='me').get()['login']

        self.access_token, self.refresh_token = access_token, refresh_token
        user_credentials = {"access_token": access_token, "refresh_token": refresh_token}
        self.credential_manager.set_user_credentials(self.__class__, self.uid, user_credentials)

    def _set_app_folder_id(self):
        box_root_folder = self.client.folder(self.BOX_ROOT_ID)

        def inner_folder_setup():
            try:  # make an app-specific folder if one does not already exist
                _, self.folder_id, _ = box_root_folder.create_subfolder(self.ROOT_DIR)
            except BoxAPIException:
                self.folder_id = self._get_id(self.ROOT_DIR, [box_root_folder], "folder")

        self.refresh_exception_handler(inner_folder_setup)

    def _connect(self, user_credentials):
        # if this came from cache, it is a json string that needs to be converted
        if type(user_credentials) in [unicode, str]:
            user_credentials = json.loads(user_credentials)

        self.access_token, self.refresh_token = user_credentials["access_token"], user_credentials["refresh_token"]
        self.client_id, self.client_secret = self._get_app_credentials()

        oauth = OAuth2(client_id=self.client_id,
                       client_secret=self.client_secret,
                       store_tokens=self._store_user_tokens,
                       access_token=self.access_token,
                       refresh_token=self.refresh_token)
        
        self.client = Client(oauth)
        self._set_app_folder_id()
        self._store_user_tokens(self.access_token, self.refresh_token)

    @property
    def uid(self):
        return self.email

    def _remove_from_cache(self, name):
        try:
            del self.id_cache[name]
        except KeyError:
            pass  # indicates that the file was created with a different instance

    def _get_id(self, name, ancestor_folders, result_type):
        def inner_search():
            return  self.client.search(name,
                                       limit=1, 
                                       offset=0,
                                       ancestor_folders=ancestor_folders,
                                       result_type=result_type,
                                       content_types="name")

        search_results = self.refresh_exception_handler(inner_search)
        
        if len(search_results) == 0:
            try:
                return self.id_cache[name]
            except KeyError:
                raise exceptions.ProviderOperationFailure(self)
        else:
            self._remove_from_cache(name)
            return search_results[0].object_id

    def _get_box_file(self, filename):
        app_folder = self.client.folder(self.folder_id)
        return self.client.file(self._get_id(filename, [app_folder], "file"))

    def get(self, filename):
        def inner_get():
            box_file = self._get_box_file(filename)
            return box_file.content()
        
        return self.refresh_exception_handler(inner_get)

    def put(self, filename, data):
        data_stream = StringIO(data)

        def inner_put():
            if filename in self.id_cache:
                existing_file = self.client.file(self.id_cache[filename])
            else:
                try:    
                    app_folder = self.client.folder(self.folder_id)     
                    new_file = app_folder.upload_stream(data_stream, filename)
                    self.id_cache[filename] = new_file.object_id
                    return
                except BoxAPIException:
                    existing_file = self.client.file(self._get_id(filename, [app_folder], "file"))
                    self.id_cache[filename] = existing_file.object_id
            existing_file.update_contents_with_stream(data_stream)

        self.refresh_exception_handler(inner_put)

    def delete(self, filename):
        def inner_delete():
            box_file = self._get_box_file(filename)
            self._remove_from_cache(filename)
            box_file.delete()

        self.refresh_exception_handler(inner_delete)

    def wipe(self):
        def inner_wipe():
            app_folder = self.client.folder(self.folder_id)

            files = []
            offset = 0
            while len(files) == offset:
                files += app_folder.get_items(self.MAX_BOX_LIMIT, offset=offset)
                offset += self.MAX_BOX_LIMIT

            for box_file in files:
                box_file.delete()

        self.refresh_exception_handler(inner_wipe)

