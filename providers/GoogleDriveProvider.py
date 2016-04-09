from tools.utils import parse_url
from BaseProvider import BaseProvider
import httplib2
from contextlib import contextmanager
from apiclient import discovery
from custom_exceptions import exceptions
from oauth2client import client
from apiclient.http import MediaIoBaseUpload
from apiclient.errors import HttpError
import io


class GoogleDriveProvider(BaseProvider):
    SCOPE = 'https://www.googleapis.com/auth/drive.file'

    @staticmethod
    def provider_name():
        return "Google Drive"

    @staticmethod
    def load_cached_providers(credential_manager):
        credentials = credential_manager.get_user_credentials(GoogleDriveProvider.provider_name())
        providers = []
        failed_ids = []
        for provider_id, json_str in credentials.items():
            gd_provider = GoogleDriveProvider(credential_manager)
            try:
                credentials = client.OAuth2Credentials.from_json(json_str)
                gd_provider._connect(credentials)
                providers.append(gd_provider)
            except:
                failed_ids.append(provider_id)
        return providers, failed_ids

    def __init__(self, credential_manager):
        """
        Initialize a google drive provider.
        Not functional until start_connection and finish_connection are called.
        Args: credential_manager, a credential_manager with information about GoogleDriveProviders
        """
        super(GoogleDriveProvider, self).__init__(credential_manager)

    @contextmanager
    def exception_handler(self):
        try:
            yield
        except exceptions.ProviderFailure:
            raise
        except HttpError as e:
            if e.resp.status in [401, 403]:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)
        except httplib2.ServerNotFoundError:
            raise exceptions.ConnectionFailure(self)
        except Exception:
            raise exceptions.ProviderOperationFailure(self)

    def start_connection(self):
        """
        Initiate a new connection to Google.
        Returns: a url that allows the user to log in
        Raises: IOError if there was a problem reading app credentials
                ProviderOperationFailure if there was a problem starting flow
        """
        try:
            credentials = self.credential_manager.get_app_credentials(self.provider_name())
            client_id, client_secret = credentials["client_id"], credentials["client_secret"]
        except (AttributeError, ValueError):
            raise IOError("No valid app credentials found!")

        with self.exception_handler():
            self.flow = client.OAuth2WebServerFlow(client_id, client_secret, self.SCOPE, redirect_uri="http://localhost")
            authorize_url = self.flow.step1_get_authorize_url()

        return authorize_url

    def finish_connection(self, url):
        """
        Finalize the connection to Google
        Args: url - a localhost url, resulting from a redirect after start_connection
        """
        params = parse_url(url)

        with self.exception_handler():
            credentials = self.flow.step2_exchange(params['code'])
        self._connect(credentials)

    def _connect(self, credentials):
        with self.exception_handler():
            http = credentials.authorize(httplib2.Http())
            self.service = discovery.build('drive', 'v3', http=http)

            self.email = self.service.about().get(fields="user").execute()["user"]["emailAddress"]

        self.credential_manager.set_user_credentials(self.provider_name(), self.uid, credentials.to_json())

    @property
    def uid(self):
        return self.email

    def _get_id(self, filename):
        query = "name = '%s' and mimeType = 'text/plain' and trashed = false" % filename

        files = self.service.files().list(q=query).execute()["files"]
        if len(files) == 0:
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

            metadata = {'name': filename}

            self.service.files().create(body=metadata, media_body=media).execute()

    def get_capacity(self):
        with self.exception_handler():
            about = gd.service.about().get(fields='storageQuota').execute()
            storageInfo = about['storageQuota']

            used_space = int(storageInfo['usage'])
            total_allocated_space = int(storageInfo['limit'])

            return used_space, total_allocated_space

    def delete(self, filename):
        with self.exception_handler():
            file_id = self._get_id(filename)
            if file_id is None:
                raise exceptions.ProviderOperationFailure(self)

            self.service.files().delete(fileId=file_id).execute()

    def wipe(self):
        with self.exception_handler():
            files = self.service.files().list().execute()["files"]
            for file in files:
                self.service.files().delete(fileId=file['id']).execute()
