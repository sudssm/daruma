import httplib2
import tempfile
import os

from BaseProvider import BaseProvider
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import argparse
from apiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io


SCOPES = 'https://www.googleapis.com/auth/drive.file'
GDRIVE_CLIENT_SECRET_FILE = 'gdrive_client_secret.json'
CREDENTIAL_DIR = '.credentials'
APPLICATION_NAME = 'Trust No One'
MIME_TYPE = 'application/vnd.google-apps.file'

def get_credentials():
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
        print('Storing credentials to ' + credential_path)

    return credentials

class GoogleDriveProvider(BaseProvider):
    def __init__(self, folder_ID=None):
        credentials = get_credentials()
        http = credentials.authorize(httplib2.Http())
        self.service = discovery.build('drive', 'v3', http=http)
        self.folder_ID = folder_ID
        # key: filename, value: file ID
        self.file_index = {}

    def connect(self):
        # check folder validity
        try:
            if self.folder_ID:
                response = self.service.files().list(q="name='%s'"%APPLICATION_NAME).execute()
                for f in response.get('files',[]):
                    if f['id'] == self.folder_ID:
                        # find a matching folder. create file index
                        response = self.service.files().list(q="'%s' in parents"%self.folder_ID).execute()
                        for f in response.get('files',[]):
                            self.file_index[f['title']] = f['id']
                        return
            
            # Create new folder: folder does not exist or no folder ID
            file_metadata = {
                'name' : APPLICATION_NAME,
                'mimeType' : 'application/vnd.google-apps.folder'
            }
            f = self.service.files().create(body=file_metadata,
                                                fields='id').execute()
            self.folder_ID = f.get('id')
            print 'Folder ID: %s' % f.get('id')
        except Exception as e:
            pass

    def _download_file(self, filename):
        request = drive_service.files().export_media(fileId=file_id,
                                                     mimeType='text/plain')
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print "Download %d%%." % int(status.progress() * 100)
        print fh
        return fh


    def get(self, filename):
        try:
            if filename not in self.file_index:
                print "file not exist"
            else:
                file_id = self.file_index[filename]
            print "here", file_id
            print self.service.files().get_media(fileId=file_id).execute()
            #print self._download_file(filen)
        except Exception as e:
            print e.message


    def put(self, filename, data):
        try:
            fh = io.BytesIO(data)
            media = MediaIoBaseUpload(fh,
                                    mimetype='text/plain',
                                    resumable=False)

            f = self.service.files().create(media_body=media).execute()

            self.file_index[filename] = f.get('id')
            print 'File ID: ' + f.get('id')
        except Exception as e:
            print e.message

        

    def delete(self, filename):
        pass

    def wipe (self):
        pass

