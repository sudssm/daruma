from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider
import requests


class TestServerProvider(BaseProvider):
    @staticmethod
    def type():
        return "Demo Server"

    @staticmethod
    def load_cached_providers(credential_manager):
        credentials = credential_manager.get_user_credentials(__name__)
        print credentials
        providers = []
        failed_hosts = []
        for host in credentials.keys():
            try:
                [hostname, port] = host.lstrip("http://").split(":")
                providers.append(TestServerProvider(credential_manager, hostname, port))
            except:
                failed_hosts.append(host)
        return providers, failed_hosts

    def __init__(self, credential_manager, server_hostname, server_port=80):
        """
        Initialize a connection to an existing demo server provider

        Args:
            credential_manager, a credential_manager to store user credentials
            server_hostname: The url where the demo server is running
            server_port: The port where the demo server is running
        """
        super(TestServerProvider, self).__init__(credential_manager)
        self.host = "http://" + server_hostname + ":" + str(server_port)
        self._connect()

    def _get_json(self, path):
        try:
            r = requests.get(self.host + "/" + path)
        except:
            raise exceptions.ConnectionFailure(self)
        try:
            return r.json()
        except:
            raise exceptions.ProviderOperationFailure(self)

    def _connect(self):
        try:
            assert self._get_json("")['connected'] is True
        except KeyError:
            raise exceptions.ProviderOperationFailure(self)

        self.credential_manager.set_user_credentials(__name__, self.host, None)

    @property
    def id(self):
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

    @property
    def expose_to_client(self):
        return True
