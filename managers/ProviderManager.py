from managers.CredentialManager import CredentialManager
from providers.DropboxProvider import DropboxProvider
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from providers.TestProvider import TestProvider
from demo_provider.client.TestServerProvider import TestServerProvider


class ProviderManager():
    """
    A manager for constructing providers and performing provider-related operations
    """
    def __init__(self):
        """
        Setup a provider manager with a new default CredentialManager
        """
        self.provider_classes = [DropboxProvider, LocalFilesystemProvider, TestProvider, TestServerProvider]
        self.credential_manager = CredentialManager()
        self.credential_manager.load()

    def load_all_providers_from_credentials(self):
        """
        Get all providers of exposed types that can be loaded from the underlying credential_manager
        Returns (cached_providers, failed_ids)
            cached_providers: a list of loaded provider objects
            failed_ids: the uuids of providers that failed to load
        """
        def flatten(list_of_lists):
            return [item for sublist in list_of_lists for item in sublist]

        providers_and_errors = map(lambda provider_class: provider_class.load_cached_providers(self.credential_manager), self.provider_classes)

        return tuple(map(flatten, zip(*providers_and_errors)))

    def start_dropbox_connection(self):
        """
        Returns the login url for Dropbox
        Calling this additional times invalidates any previous unfinished flows
        """
        self.temp_dropbox = DropboxProvider(self.credential_manager)
        return self.temp_dropbox.start_connection()

    def finish_dropbox_connection(self, localhost_url):
        """
        Args: localhost_url, the url resulting from redirect after start_dropbox_connection
        Returns: a functional DropboxProvider
        Raises ProviderOperationFailure
        """
        if self.temp_dropbox is None:
            raise ValueError("Call start_dropbox_connection first!")
        temp_dropbox = self.temp_dropbox
        self.temp_dropbox = None
        temp_dropbox.finish_connection(localhost_url)
        return temp_dropbox

    def make_local(self, path):
        """
        Args: path, the path on the local filesystem to use for the provider
        Returns: a functional LocalFilesystemProvider
        Raises ProviderOperationFailure
        """
        return LocalFilesystemProvider(self.credential_manager, path)

    def make_test(self, path):
        """
        Args: path, the path on the local filesystem to use for the test provider
        Returns: a functional TestProvider
        Raises ProviderOperationFailure
        """
        return TestProvider(self.credential_manager, path)

    def make_test_server(self, hostname, port):
        """
        Args:
            hostname: the host where the test server is running
            port: the port of the test provider
        Returns: a functional TestServerProvider
        Raises ProviderOperationFailure
        """
        return TestProvider(self.credential_manager, hostname, port)
