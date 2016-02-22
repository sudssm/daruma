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
GDRIVE_CLIENT_SECRET_FILE = 'gdrive_client_secret.json'
CREDENTIAL_DIR = '.credentials'
APPLICATION_NAME = 'Trust No One'


class GoogleDriveProvider(BaseProvider):
    
    def __init__(self):
        credentials = GoogleDriveProvider.get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)
        
        # key: filename, value: file ID
        self.file_index = {}


    @staticmethod
    def get_credentials():
        try:
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
        except HttpError as e:
            # TODO: Duplicate exception handling
            if e.resp.status in [401,403]:
                raise exceptions.AuthFailure(None)
            raise exceptions.ProviderOperationFailure(None)
        except httplib2.ServerNotFoundError:
            raise exceptions.ConnectionFailure(None)
        except Exception:
            raise exceptions.LibraryException


    @contextmanager
    def exception_handler(self):
        try:
            yield
        except HttpError as e:
            if e.resp.status in [401,403]:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)
        except httplib2.ServerNotFoundError:
            raise exceptions.ConnectionFailure(self)
        except Exception:
            raise exceptions.LibraryException


    def _update_cache(self):
        with self.exception_handler():
            response = self.service.files().list(q="name='%s'"%self.ROOT_DIR).execute()
            results = response.get('files',[])
            f = results[0]
            self.folder_ID = f['id']
            response = self.service.files().list(q="'%s' in parents"%self.folder_ID).execute()
            for f in response.get('files',[]):
                self.file_index[f['title']] = f['id']
        

    def connect(self):
        # check folder validity
        with self.exception_handler():
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
        with self.exception_handler():
            file_id = self._get_id(filename)
            if file_id is None:
                # file not exist
                raise Exception # TODO

            return self.service.files().get_media(fileId=file_id).execute()


    def put(self, filename, data):
        with self.exception_handler():
            fh = io.BytesIO(data)

            # TODO 
            media = MediaIoBaseUpload(fh,
                                    mimetype='text/plain',
                                    resumable=False)

            file_metadata = {
                'name' : filename,
                'mimeType' : 'application/vnd.google-apps.file',
                'parents':[self.folder_ID]
            }

            f = self.service.files().create(body=file_metadata,media_body=media,fields='id').execute()

            self.file_index[filename] = f.get('id')


    def delete(self, filename):
        with self.exception_handler():
            file_id = self._get_id(filename)
            if file_id is None:
                # file not exist
                raise Exception # TODO

            self.service.files().delete(fileId=file_id).execute()


    def wipe (self):
        self.delete(self.ROOT_DIR)

