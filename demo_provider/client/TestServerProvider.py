from custom_exceptions import exceptions
from providers.UnauthenticatedProvider import UnauthenticatedProvider
from contextlib import contextmanager
import requests


class TestServerProvider(UnauthenticatedProvider):
    # the amount of time to wait on a request, in seconds
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
            raise exceptions.ProviderOperationFailure(self)

    def __init__(self, credential_manager):
        """
        Initialize a connection to an existing demo server provider

        Args:
            credential_manager, a credential_manager to store user credentials
        """
        super(TestServerProvider, self).__init__(credential_manager)

    def _do_get(self, path):
        response = requests.get(self.host + "/" + path, timeout=self.TIMEOUT)
        assert response.status_code == 200
        return response

    def connect(self, url):
        """
        Connect to the demo server at url
        url: the fully defined url (http://hostname:port) where the server is running
        """
        self.host = url
        with self.exception_handler():
            self._do_get("")

        self.credential_manager.set_user_credentials(self.__class__, self.host, None)

    @property
    def uid(self):
        return self.host

    def get(self, filename):
        with self.exception_handler():
            response = self._do_get("get/" + filename)
            return response.content

    def put(self, filename, data):
        with self.exception_handler():
            response = requests.post(self.host + "/put", files={filename: data}, timeout=self.TIMEOUT)
            assert response.status_code == 200

    def delete(self, filename):
        with self.exception_handler():
            self._do_get("delete/" + filename)

    def wipe(self):
        with self.exception_handler():
            self._do_get("wipe")
