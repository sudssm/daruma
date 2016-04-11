from providers.BaseProvider import BaseProvider


class OAuthProvider(BaseProvider):
    """
    Stub for OAuthProviders, defining the flow for connection
    OAuth Providers use the value portion of the CredentialManager (key,value) store to store user tokens
    """
    @classmethod
    def load_cached_providers(cls, credential_manager):
        credentials = credential_manager.get_user_credentials(cls)
        providers = []
        failed_ids = []
        for provider_id, credential in credentials.items():
            provider = cls(credential_manager)
            try:
                provider._connect(credential)
                providers.append(provider)
            except:
                failed_ids.append((cls.provider_identifier(), provider_id))
        return providers, failed_ids

    def start_connection(self):
        """
        Initiate a new connection to the provider. Invalidates any urls returned by calls to start_connection
        Returns: a url that allows the user to log in
        Raises: IOError if there was a problem reading app credentials
                ProviderOperationFailure if there was a problem starting flow
        """
        raise NotImplementedError

    def finish_connection(self, url):
        """
        Finalize the connection to the provider
        Args: url - a localhost url, resulting from a redirect after start_connection
        Raises ProviderOperationFailure
        """
        raise NotImplementedError

    def _connect(self, credential):
        """
        Connects to the provider represented by credential
        Raises ProviderOperationFailure
        """
        raise NotImplementedError
