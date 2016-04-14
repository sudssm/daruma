from custom_exceptions import exceptions
from providers.UnauthenticatedProvider import UnauthenticatedProvider
from contextlib import contextmanager
import requests


class TestServerProvider(UnauthenticatedProvider):
    TIMEOUT = 0.1

    @classmethod
    def provider_identifier(cls):
        return "demoserver"

    @classmethod
    def provider_name(cls):
        return "Demo Server"

    @classmethod
    def get_configuration_label(cls):
        return "Server URL"

    @contextmanager
    def exception_handler(self):
        try:
            yield
        except requests.ConnectionError:
            raise exceptions.ConnectionFailure(self)
        except:
            raise exceptions.ProviderFailure(self)

    def __init__(self, credential_manager):
        """
        Initialize a connection to an existing demo server provider

        Args:
            credential_manager, a credential_manager to store user credentials
        """
        super(TestServerProvider, self).__init__(credential_manager)

    def _get_json(self, path):
        with self.exception_handler():
            r = requests.get(self.host + "/" + path, timeout=self.TIMEOUT)
            return r.json()

    def connect(self, url):
        """
        Connect to the demo server at url
        url: the fully defined url (http://hostname:port) where the server is running
        """
        self.host = url
        with self.exception_handler():
            assert self._get_json("")['connected'] is True

        self.credential_manager.set_user_credentials(self.__class__, self.host, None)

    @property
    def uid(self):
        return self.host

    def get(self, filename):
        with self.exception_handler():
            return self._get_json("get/" + filename)['data']

    def put(self, filename, data):
        with self.exception_handler():
            r = requests.post(self.host + "/put", files={filename: data}, timeout=self.TIMEOUT)
            assert r.json()['success'] is True

    def delete(self, filename):
        with self.exception_handler():
            assert self._get_json("delete/" + filename)['success'] is True

    def wipe(self):
        with self.exception_handler():
            assert self._get_json("wipe")['success'] is True
