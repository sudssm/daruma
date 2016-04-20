from managers.CredentialManager import CredentialManager
from providers.DropboxProvider import DropboxProvider
from providers.GoogleDriveProvider import GoogleDriveProvider
from providers.BoxProvider import BoxProvider
from providers.OneDriveProvider import OneDriveProvider
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from providers.OAuthProvider import OAuthProvider
from providers.UnauthenticatedProvider import UnauthenticatedProvider
from demo_provider.client.TestServerProvider import TestServerProvider
from tools.utils import run_parallel


class ProviderManager():
    """
    A manager for constructing providers and performing provider-related operations
    """
    # the classes of all available providers
    PROVIDER_CLASSES = [DropboxProvider, GoogleDriveProvider, BoxProvider, OneDriveProvider, LocalFilesystemProvider, TestServerProvider]

    def __init__(self):
        """
        Setup a provider manager with a new default CredentialManager
        """
        self.credential_manager = CredentialManager()
        self.credential_manager.load()
        self.tmp_oauth_providers = {}  # Stores data for in-flight OAuth transactions

    def get_provider_classes(self):
        """
        Returns all available provider classes in a list.
        """
        return self.PROVIDER_CLASSES[:]

    def get_provider_classes_by_kind(self):
        """
        Get all available provider classes
        Returns a tuple (oauth_providers, unauth_providers)
            oauth_providers: a map from provider_identifier to provider class that follows the oauth flow
            unauth_providers: a map from provider_identifier to provider class that follows the unauth flow
        """
        provider_classes = self.get_provider_classes()
        oauth_providers = {cls.provider_identifier(): cls for cls in provider_classes if issubclass(cls, OAuthProvider)}
        unauth_providers = {cls.provider_identifier(): cls for cls in provider_classes if issubclass(cls, UnauthenticatedProvider)}
        return oauth_providers, unauth_providers

    def load_all_providers_from_credentials(self):
        """
        Get all providers of exposed types that can be loaded from the underlying credential_manager
        Returns (cached_providers, failed_ids)
            cached_providers: a list of loaded provider objects
            failed_ids: the uuids of providers that failed to load
        """
        def flatten(list_of_lists):
            return [item for sublist in list_of_lists for item in sublist]

        providers_and_errors = []

        def load_cached_by_class(provider_class):
            providers_and_errors.append(provider_class.load_cached_providers(self.credential_manager))

        provider_classes = self.get_provider_classes()
        run_parallel(load_cached_by_class, map(lambda provider_class: [provider_class], provider_classes))

        return tuple(map(flatten, zip(*providers_and_errors)))

    def start_oauth_connection(self, provider_class):
        """
        Start a connection for the OAuthProvider of the specified class
        Args: provider_class: the class of the provider to be created
        Returns the login url for the provider
        Calling this additional times invalidates any previous unfinished flows for this class
        """
        provider = provider_class(self.credential_manager)
        self.tmp_oauth_providers[provider_class] = provider
        return provider.start_connection()

    def finish_oauth_connection(self, provider_class, localhost_url):
        """
        Finish the connection for the OAuthProvider of the specified class
        Args:
            provider_class: the class of the provider to be created
            localhost_url, the url resulting from redirect after start_oauth_connection(provider_class)
        Returns: a functional provider
        Raises ProviderOperationFailure
        """
        provider = self.tmp_oauth_providers.get(provider_class)
        if provider is None:
            raise ValueError("Call start_oauth_connection with this class first!")
        self.tmp_oauth_providers[provider_class] = None

        provider.finish_connection(localhost_url)
        return provider

    def make_unauth_provider(self, provider_class, provider_id):
        """
        Args:
            provider_class: the class of the provider to be created
            provider_id: the identifier of the provider to be created
        Make an Unauthenticated provider with the specified class and provider_id
        Raises ProviderOperationFailure
        """
        provider = provider_class(self.credential_manager)
        provider.connect(provider_id)
        return provider
