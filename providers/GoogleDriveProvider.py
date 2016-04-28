import logging
from tools.utils import parse_url
from providers.OAuthProvider import OAuthProvider
import httplib2
from contextlib import contextmanager
from apiclient import discovery, http
from custom_exceptions import exceptions
from oauth2client import client
from apiclient.http import MediaIoBaseUpload
from apiclient.errors import HttpError
import io

logger = logging.getLogger("daruma")

class GoogleDriveProvider(OAuthProvider):
    SCOPE = ['https://www.googleapis.com/auth/drive.appfolder']
    ROOT_DIR = "appDataFolder"

    @classmethod
    def provider_identifier(cls):
        return "googledrive"

    @classmethod
    def provider_name(cls):
        return "Google Drive"

    def __init__(self, credential_manager):
        """
        Initialize a google drive provider.
        Not functional until start_connection and finish_connection are called.
        Args: credential_manager, a credential_manager with information about GoogleDriveProviders
        """
        super(GoogleDriveProvider, self).__init__(credential_manager)
        self.email = ""

    @contextmanager
    def exception_handler(self):
        try:
            yield
        except exceptions.ProviderFailure:
            raise
        except HttpError as e:
            logger.error("HttpError in GoogleDriveProvider: %s", e)
            if e.resp.status in [401, 403]:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)
        except httplib2.ServerNotFoundError as e:
            logger.error("ServerNotFoundError in GoogleDriveProvider: %s", e)
            raise exceptions.ConnectionFailure(self)
        except Exception as e:
            logger.error("General error in GoogleDriveProvider: %s", e)
            raise exceptions.ProviderOperationFailure(self)

    def start_connection(self):
        credentials = self.app_credentials
        client_id, client_secret = credentials["client_id"], credentials["client_secret"]

        with self.exception_handler():
            self.flow = client.OAuth2WebServerFlow(client_id, client_secret, self.SCOPE, redirect_uri=self.get_oauth_redirect_url())
            authorize_url = self.flow.step1_get_authorize_url()

        return authorize_url

    def finish_connection(self, url):
        params = parse_url(url)

        with self.exception_handler():
            credentials = self.flow.step2_exchange(params['code'])
        self._connect(credentials)

    def _connect(self, credentials):
        # if this came from cache, it is a json string that needs to be converted
        if type(credentials) in [unicode, str]:
            credentials = client.OAuth2Credentials.from_json(credentials)

        with self.exception_handler():
            # Create a new Http() object for every request to ensure thread safety
            def build_request(old_http, *args, **kwargs):
                new_http = credentials.authorize(httplib2.Http())
                return http.HttpRequest(new_http, *args, **kwargs)

            self.service = discovery.build('drive', 'v3', requestBuilder=build_request)

            self.email = self.service.about().get(fields="user").execute()["user"]["emailAddress"]

        self.credential_manager.set_user_credentials(self.__class__, self.uid, credentials.to_json())

    @property
    def uid(self):
        return self.email

    def _get_id(self, filename):
        query = "name = '%s' and mimeType = 'text/plain' and trashed = false" % filename

        files = self.service.files().list(q=query, spaces=self.ROOT_DIR).execute()["files"]
        if len(files) == 0:
            logger.error("Error in GoogleDriveProvider: no file with id %s", filename)
            raise exceptions.ProviderOperationFailure(self)

        # assume that there is only one file with given name and type
        return files[0]['id']

    def get(self, filename):
        with self.exception_handler():
            file_id = self._get_id(filename)
            return self.service.files().get_media(fileId=file_id).execute()

    def put(self, filename, data):
        with self.exception_handler():
            fh = io.BytesIO(data)
            media = MediaIoBaseUpload(fh, mimetype='text/plain', resumable=False)

            metadata = {
                'name': filename,
                'parents': [self.ROOT_DIR]
            }

            self.service.files().create(body=metadata, media_body=media, fields='id').execute()

    def delete(self, filename):
        with self.exception_handler():
            file_id = self._get_id(filename)
            if file_id is None:
                logger.error("Error in GoogleDriveProvider delete: no file with name %s", filename)
                raise exceptions.ProviderOperationFailure(self)

            self.service.files().delete(fileId=file_id).execute()

    def wipe(self):
        with self.exception_handler():
            files = self.service.files().list(spaces=self.ROOT_DIR).execute()["files"]
            for file in files:
                self.service.files().delete(fileId=file['id']).execute()
