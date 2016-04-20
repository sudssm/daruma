from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT
from providers.BaseProvider import BaseProvider


class OAuthProvider(BaseProvider):
    """
    Stub for OAuthProviders, defining the flow for connection
    OAuth Providers use the value portion of the CredentialManager (key,value) store to store user tokens
    """
    _app_credentials = None

    @classmethod
    def get_oauth_redirect_url(cls):
        return ("http://" + INTERNAL_SERVER_HOST + ":" +
                str(INTERNAL_SERVER_PORT) + "/providers/add/" +
                cls.provider_identifier() + "/finish")

    @classmethod
    def load_from_credential(cls, credential_manager, provider_id):
        credential = credential_manager.get_user_credentials(cls)[provider_id]
        provider = cls(credential_manager)
        provider._connect(credential)

        return provider

    @property
    def app_credentials(self):
        """
        A dictionary with keys 'client_id' and client_secret'
        """
        if self._app_credentials is None:
            try:
                self._app_credentials = self.credential_manager.get_app_credentials(self.__class__)
                assert self._app_credentials is not None
            except AssertionError:
                raise IOError("No valid app credentials found!")
        return self._app_credentials

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
