from providers.BaseProvider import BaseProvider


class UnauthenticatedProvider(BaseProvider):
    """
    Stub for UnauthenticatedProviders
    UnauthenticatedProviders don't use the value part of the (key, value) stored in CredentialManager
    """
    @classmethod
    def load_from_credential(cls, credential_manager, provider_id):
        provider = cls(credential_manager)
        provider.connect(provider_id)
        return provider

    def connect(self, provider_id):
        """
        Connect to the provider represented by provider_id
        Two providers with different provider_ids must be different
        Raises ProviderFailure
        """
        raise NotImplementedError

    @classmethod
    def get_configuration_label(cls):
        """
        Returns a string title for the provider_id argument to connect().
        This will be displayed to users to help them select a suitable id (e.g.
        file path or server address).
        """
        raise NotImplementedError
