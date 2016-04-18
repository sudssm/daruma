import onedrivesdk
from onedrivesdk.helpers import GetAuthCodeServer
from contextlib import contextmanager
from providers.BaseProvider import BaseProvider


class OneDriveProvider(BaseProvider):
    @classmethod
    def provider_identifier(cls):
        return "onedrive"

    @classmethod
    def provider_name(cls):
        return "OneDrive"

    def __init__(self, credential_manager):
        """
        Initialize a onedrive provider.
        Not functional until start_connection and finish_connection are called.
        Args: credential_manager, a credential_manager with information about OneDriveProviders
        """
        super(OneDriveProvider, self).__init__(credential_manager)

    @contextmanager
    def exception_handler(self):
        # Website information: https://dev.onedrive.com/misc/errors.htm
        pass

    def start_connection(self):
        """
        """
        try:
            credentials = self.credential_manager.get_app_credentials(self.__class__)
            client_id = credentials['client_id']
        except (AttributeError, ValueError):
            raise IOError("No valid app credentials found!")

        self.client = onedrivesdk.get_default_client(client_id=client_id,
                                                    scopes=['wl.signin',
                                                            'wl.emails',
                                                            'wl.offline_access',
                                                            'onedrive.appfolder'])
        auth_url = self.client.auth_provider.get_auth_url("http://localhost")
        return auth_url

    def finish_connection(self, url):
        """
        """
        params = parse_url(url)
        self._connect(params['code'])

    def _connect(self, auth_code):
        try:
            credentials = self.credential_manager.get_app_credentials(self.__class__)
            client_secret = credentials['client_secret']
        except (AttributeError, ValueError):
            raise IOError("No valid app credentials found!")

        self.client.auth_provider.authenticate(auth_code, "http://localhost", client_secret)
        self.credential_manager.set_user_credentials(self.__class__, self.uid, auth_code)
        # set self.email

    @property
    def uid(self):
        return self.email

    def _get_id(self, filename):
        pass

    def get(self, filename):
        pass

    def put(self, filename, data):
        # TODO work out put request
        # currently use onedrive_tmp.txt
        with open('./onedrive_tmp.txt', 'w') as f:
            f.write(data)
        self.client.item(drive="me", id="root").children[filename].upload("./onedrive_tmp.txt")


    def get_capacity(self):
        pass

    def delete(self, filename):
        item_id = self._get_id(filename)
        self.client.item(id=item_id).delete()

    def wipe (self):
        pass

