from providers.BaseProvider import BaseProvider


class UnauthenticatedProvider(BaseProvider):
    """
    Stub for UnauthenticatedProviders
    UnauthenticatedProviders don't use the value part of the (key, value) stored in CredentialManager
    """
    @classmethod
    def load_cached_providers(cls, credential_manager):
        credentials = credential_manager.get_user_credentials(cls.provider_name())
        providers = []
        failed_ids = []
        for provider_id in credentials.keys():
            provider = cls(credential_manager)
            try:
                provider.connect(provider_id)
                providers.append(provider)
            except:
                failed_ids.append((cls.provider_name(), provider_id))
        return providers, failed_ids

    def connect(self, provider_id):
        """
        Connect to the provider represented by provider_id
        Two providers with different provider_ids must be different
        Raises ProviderFailure
        """
        raise NotImplementedError
