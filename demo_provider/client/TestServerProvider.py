from custom_exceptions import exceptions
from providers.UnauthenticatedProvider import UnauthenticatedProvider
import requests


class TestServerProvider(UnauthenticatedProvider):
    @classmethod
    def provider_identifier(cls):
        return "demoserver"

    @classmethod
    def provider_name(cls):
        return "Demo Server"

    def __init__(self, credential_manager):
        """
        Initialize a connection to an existing demo server provider

        Args:
            credential_manager, a credential_manager to store user credentials
        """
        super(TestServerProvider, self).__init__(credential_manager)

    def _get_json(self, path):
        try:
            r = requests.get(self.host + "/" + path)
        except:
            raise exceptions.ConnectionFailure(self)
        try:
            return r.json()
        except:
            raise exceptions.ProviderOperationFailure(self)

    def connect(self, url):
        """
        Connect to the demo server at url
        url: the fully defined url (http://hostname:port) where the server is running
        """
        self.host = url
        try:
            assert self._get_json("")['connected'] is True
        except KeyError:
            raise exceptions.ProviderOperationFailure(self)

        self.credential_manager.set_user_credentials(self.__class__, self.host, None)

    @property
    def uid(self):
        return self.host

    def get(self, filename):
        try:
            return self._get_json("get/" + filename)['data']
        except KeyError:
            raise exceptions.ProviderOperationFailure(self)

    def put(self, filename, data):
        try:
            r = requests.post(self.host + "/put", files={filename: data})
            assert r.json()['success'] is True
        except (KeyError, AssertionError):
            raise exceptions.ProviderOperationFailure(self)

    def delete(self, filename):
        try:
            assert self._get_json("delete/" + filename)['success'] is True
        except (KeyError, AssertionError):
            raise exceptions.ProviderOperationFailure(self)

    def wipe(self):
        try:
            assert self._get_json("wipe")['success'] is True
        except (KeyError, AssertionError):
            raise exceptions.ProviderOperationFailure(self)
