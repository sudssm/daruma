import httplib2
import os

from BaseProvider import BaseProvider
from contextlib import contextmanager
from apiclient import discovery
from custom_exceptions import exceptions
import oauth2client
from oauth2client import client, tools
import argparse
from apiclient.http import MediaIoBaseUpload
from apiclient.errors import HttpError
import io


SCOPES = 'https://www.googleapis.com/auth/drive.file'
GDRIVE_CLIENT_SECRET_FILE = '/Users/raylei/Desktop/Stuff/senior_design/trust-no-one/providers/gdrive_client_secret.json'
CREDENTIAL_DIR = '/Users/raylei/Desktop/Stuff/senior_design/trust-no-one/providers/.credentials'
APPLICATION_NAME = 'Trust No One'
REDIRECT_URL = "127.0.0.1" # Localhost

class GoogleDriveProvider(BaseProvider):
    
    def __init__(self):
        credentials = GoogleDriveProvider.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)
        
        # key: filename, value: file ID
        self.file_index = {}
        self.connect()

    @staticmethod
    @contextmanager
    def exception_handler(provider):
        try:
            yield
        # except HttpError as e:
            # if e.resp.status in [401,403]:
            #     raise exceptions.AuthFailure(provider)
            # raise exceptions.ProviderOperationFailure(provider)
        except httplib2.ServerNotFoundError:
            raise exceptions.ConnectionFailure(provider)
        # except Exception:
        #     raise exceptions.LibraryException

    @staticmethod
    def get_credentials():
        with GoogleDriveProvider.exception_handler(None):
            # required python 2.7
            flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

            if not os.path.exists(CREDENTIAL_DIR):
                os.makedirs(CREDENTIAL_DIR)

            credential_path = os.path.join(CREDENTIAL_DIR, 'user_credentials.json')

            # store user credentials in a file
            store = oauth2client.file.Storage(credential_path)
            credentials = store.get()

            if not credentials or credentials.invalid:
                flow = client.flow_from_clientsecrets(GDRIVE_CLIENT_SECRET_FILE, SCOPES)
                flow.user_agent = APPLICATION_NAME
                credentials = tools.run_flow(flow, store, flags)

            return credentials
    


    def _update_cache(self):
        with GoogleDriveProvider.exception_handler(self):
            response = self.service.files().list(q="name='%s'"%self.ROOT_DIR).execute()
            results = response.get('files',[])
            f = results[0]
            self.folder_ID = f['id']
            response = self.service.files().list(q="'%s' in parents"%self.folder_ID).execute()
            for f in response.get('files',[]):
                self.file_index[f['name']] = f['id']
        

    def connect(self):
        # check folder validity
        with GoogleDriveProvider.exception_handler(self):
            response = self.service.files().list(q="name='%s'"%self.ROOT_DIR).execute()
            results = response.get('files',[])

            if len(results) == 0:
                # Create new folder: folder does not exist or no folder ID
                file_metadata = {
                    'name' : self.ROOT_DIR,
                    'mimeType' : 'application/vnd.google-apps.folder'
                }
                f = self.service.files().create(body=file_metadata, fields='id').execute()
                
            else:
                # assume uniqueness of folder name
                f = results[0]
            
            self.folder_ID = f.get('id')
            self.file_index[self.ROOT_DIR] = self.folder_ID
        

    def _get_id(self, filename):
        if filename not in self.file_index:
            self._update_cache()
        return self.file_index.get(filename, None)


    def get(self, filename):
        with GoogleDriveProvider.exception_handler(self):
            file_id = self._get_id(filename)
            if file_id is None:
                # file not exist
                raise exceptions.ProviderOperationFailure(self)

            return self.service.files().get_media(fileId=file_id).execute()


    def put(self, filename, data):
        with GoogleDriveProvider.exception_handler(self):
            fh = io.BytesIO(data)

            # TODO 
            media = MediaIoBaseUpload(fh,
                                    mimetype='text/plain',
                                    resumable=False)

            file_metadata = {
                'name' : filename,
                'parents':[self.folder_ID]
            }

            f = self.service.files().create(body=file_metadata,media_body=media,fields='id').execute()

            self.file_index[filename] = f.get('id')


    def delete(self, filename):
        with GoogleDriveProvider.exception_handler(self):
            file_id = self._get_id(filename)
            if file_id is None:
                # file not exist
                raise Exception # TODO

            self.service.files().delete(fileId=file_id).execute()
            self.file_index.pop(filename, None)


    def wipe (self):
        self.delete(self.ROOT_DIR)
        self.file_index = {}
        self.connect()

