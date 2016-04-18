import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from contextlib import contextmanager
from providers.BaseProvider import BaseProvider
from providers.OneDriveProvider import OneDriveProvider
from managers.CredentialManager import CredentialManager

credential_manager = CredentialManager()
credential_manager.load()

try:
    credentials = credential_manager.get_app_credentials(OneDriveProvider)
    client_id = credentials['client_id']
except (AttributeError, ValueError):
    raise IOError("No valid app credentials found!")

client = onedrivesdk.get_default_client(client_id=client_id,
                                            scopes=['wl.signin',
                                                    'wl.emails',
                                                    'wl.offline_access',
                                                    'onedrive.appfolder'])
auth_url = client.auth_provider.get_auth_url("http://localhost")

auth_code = "M2bd80f86-58be-c858-b41e-2c858cb0be23"

# Finish connection
try:
    credentials = credential_manager.get_app_credentials(OneDriveProvider)
    client_secret = credentials['client_secret']
except (AttributeError, ValueError):
    raise IOError("No valid app credentials found!")

client.auth_provider.authenticate(auth_code, "http://localhost", client_secret)
credential_manager.set_user_credentials(OneDriveProvider, "tmp_uid", auth_code)

# test upload with file path
client.item(drive="me", id="root").children['test.txt'].upload("providers/onedrive_tmp.txt")



