from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider
import requests


class TestServerProvider(BaseProvider):
    def __init__(self, server_hostname, server_port=80):
        """
        Initialize a connection to an existing demo server provider

        Args:
            server_hostname: The url where the demo server is running
            server_port: The port where the demo server is running
        """
        self.host = "http://" + server_hostname + ":" + str(server_port)
        super(TestServerProvider, self).__init__()

    def _get_json(self, path):
        try:
            r = requests.get(self.host + "/" + path)
        except:
            raise exceptions.ConnectionFailure(self)
        try:
            return r.json()
        except:
            raise exceptions.ProviderOperationFailure(self)

    def connect(self):
        try:
            assert self._get_json("")['connected'] is True
        except KeyError:
            raise exceptions.ProviderOperationFailure(self)

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
