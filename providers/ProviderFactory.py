from OAuthRedirectServer import OAuthRedirectServer
from CredentialManager import CredentialManager
from custom_exceptions import exceptions
import threading

# Fixed port
AUTH_PORT = 51168

class ProviderFactory(object):

    @staticmethod
    def create_provider_instance(provider):
        # Check credentials
        credential = CredentialManager.getCredentials(provider)
        if credential:
            provider_instance = provider(credential)
            return provider_instance
        else:
            # no credentials stored
            raise exceptions.AuthFailure


    @staticmethod
    def get_authentication_url(provider):
        auth_url, flow = provider.new_connection_redirect(AUTH_PORT)

        # setup authentication server
        server = OAuthRedirectServer(provider.finish_connection_redirect, AUTH_PORT, dropboxflow=flow)
        auth_server_thread = threading.Thread(target=server.start, name="auth_server_thread")
        auth_server_thread.daemon = True
        auth_server_thread.start()

        # return authentication url
        return auth_url
