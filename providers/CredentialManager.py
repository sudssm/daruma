import json
from appdirs import *

APP_NAME = "Trust No One"
FILE_NAME = user_config_dir(APP_NAME) + "config.json"


class CredentialManager(object):

    @staticmethod
    def get_credentials(provider):
        """
        Get user credentials for a provider. Return None if not presented

        Args:
            provider: a provider class
        """

        credential_file = open(FILE_NAME, 'r')
        
        # load user credentials 
        try:
            credentials = json.load(credential_file)
        except ValueError:
            credentials = {}

        return credentials.get(provider.__name__)


    @staticmethod
    def update_credentials(provider, credential):
        """
        Update user credential for the provider

        Args:
            provider: a provider class
            credential: the user credential for that provider
        """

        credential_file = open(FILE_NAME, 'r+')
        try:
            credentials = json.load(credential_file)
        except ValueError:
            credentials = {}

        credentials[provider.__name__] = credential

        # overwrite file
        credential_file.seek(0)
        credential_file.write(json.dumps(credentials))
        credential_file.truncate()
        credential_file.close()

        
