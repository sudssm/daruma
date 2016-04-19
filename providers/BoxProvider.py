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
    BOX_ROOT_ID = '0'  # Box root directory has id zero
    MAX_BOX_LIMIT = 1000  # the maximum number of items returned from a Box request

    @classmethod
    def provider_identifier(cls):
        return "box"

    @classmethod
    def provider_name(cls):
        return "Box"

    def __init__(self, credential_manager):
        super(BoxProvider, self).__init__(credential_manager)
        self.id_cache = {}
        self._email, self._client_id, self._client_secret = None, None, None

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

    def refresh_on_fail(self, func):
        try:
            with self.exception_handler():
                return func()
        except exceptions.AuthFailure:
            with self.exception_handler():
                # implicitly stores refreshed tokens with _store_user_tokens callback
                self.client.auth.refresh(self.access_token)
                return func()

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

    def _store_user_tokens(self, access_token, refresh_token):
        self.access_token, self.refresh_token = access_token, refresh_token
        print "STORE"
        print access_token, refresh_token
        user_credentials = {"access_token": access_token, "refresh_token": refresh_token}
        self.credential_manager.set_user_credentials(self.__class__, self.uid, user_credentials)

    def _make_app_folder(self):
        box_root_folder = self.client.folder(self.BOX_ROOT_ID)

        def inner_folder_setup():
            try:  # make an app-specific folder if one does not already exist
                _, folder_id, _ = box_root_folder.create_subfolder(self.ROOT_DIR)
            except BoxAPIException:
                search_results = self.client.search(self.ROOT_DIR,
                                                    limit=1, 
                                                    offset=0,
                                                    ancestor_folders=[box_root_folder],
                                                    result_type="folder")
                if len(search_results) != 1:
                    raise
                folder_id = search_results[0].object_id

            self.app_folder = self.client.folder(folder_id)

        self.refresh_on_fail(inner_folder_setup)

    def _collect_items(self):
        files = []
        offset = 0
        while len(files) == offset:
            files += self.app_folder.get_items(self.MAX_BOX_LIMIT, offset=offset)
            offset += self.MAX_BOX_LIMIT
        return files

    def _prime_cache(self):
        def inner_prime_cache():
            files = self._collect_items()
            for user_file in files:
                self.id_cache[user_file.name] = user_file.object_id

        self.refresh_on_fail(inner_prime_cache)

    def _connect(self, user_credentials):
        # if this came from cache, it is a json string that needs to be converted
        if type(user_credentials) in [unicode, str]:
            user_credentials = json.loads(user_credentials)

        self.access_token, self.refresh_token = user_credentials["access_token"], user_credentials["refresh_token"]

        oauth = OAuth2(client_id=self.app_credentials["client_id"],
                       client_secret=self.app_credentials["client_secret"],
                       store_tokens=self._store_user_tokens,
                       access_token=self.access_token,
                       refresh_token=self.refresh_token)
        
        self.client = Client(oauth)

        print "CONNECT"
        print self.access_token, self.refresh_token
        self._store_user_tokens(self.access_token, self.refresh_token)

        self._make_app_folder()
        self._prime_cache()

        # print self.id_cache

    @property
    def app_credentials(self):
        """
        A dictionary with keys 'client_id' and client_secret'
        """
        if self._client_id is None or self._client_secret is None:
            try:
                credentials = self.credential_manager.get_app_credentials(self.__class__)
                self._client_id, self._client_secret = credentials["client_id"], credentials["client_secret"]
            except (KeyError, TypeError):
                raise IOError("No valid app credentials found!")
        return {"client_id": self._client_id, "client_secret": self._client_secret}

    @property
    def uid(self):
        if self._email is None:
            with self.exception_handler():
                self._email = self.client.user(user_id='me').get()['login']
        return self._email

    def get(self, filename):
        def inner_get():
            box_file = self.client.file(self.id_cache[filename])
            return box_file.content()
        
        return self.refresh_on_fail(inner_get)

    def put(self, filename, data):
        data_stream = StringIO(data)

        def inner_put():
            if filename in self.id_cache:
                existing_file = self.client.file(self.id_cache[filename])
                existing_file.update_contents_with_stream(data_stream)
            else:       
                new_file = self.app_folder.upload_stream(data_stream, filename)
                self.id_cache[filename] = new_file.object_id

        self.refresh_on_fail(inner_put)

    def delete(self, filename):
        def inner_delete():
            box_file = self.client.file(self.id_cache[filename])
            box_file.delete()
            self.id_cache.pop(filename, None)

        self.refresh_on_fail(inner_delete)

    def wipe(self):
        def inner_wipe():
            try:
                for _, file_id in self.id_cache.items():
                    box_file = self.client.file(file_id)
                    box_file.delete()
            except:
                raise
            finally:
                self.id_cache = {}

        self.refresh_on_fail(inner_wipe)

