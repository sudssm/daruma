import json
import os
from appdirs import *


APP_NAME = "Trust No One"
APP_DIR = user_config_dir(APP_NAME)
FILE_NAME = os.path.join(user_config_dir(APP_DIR), "credentials.json")


class CredentialManager(object):

    @staticmethod
    def get_credentials(provider):
        """
        Get user credentials for a provider. Return None if not presented

        Args:
            provider: a provider class
        Returns:
            The credentials for the specified provider
        """

        if not os.path.exists(FILE_NAME):
            CredentialManager.create_credential_file_if_not_exist()

        
        with open(FILE_NAME, 'r') as credential_file:        
        
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

        if not os.path.exists(FILE_NAME):
            CredentialManager.create_credential_file_if_not_exist()

        with open(FILE_NAME, 'r+') as credential_file:

            # load user credentials
            try:
                credentials = json.load(credential_file)
            except ValueError:
                credentials = {}

            credentials[provider.__name__] = credential

            # overwrite file
            credential_file.seek(0)
            credential_file.write(json.dumps(credentials))
            credential_file.truncate()

    @staticmethod
    def clear_credentials():
        if not os.path.exists(FILE_NAME):
            CredentialManager.create_credential_file_if_not_exist()

        f = open(FILE_NAME, 'w')
        f.close()

    @staticmethod
    def create_credential_file_if_not_exist():
        # create app folder if it does not exist
        if not os.path.exists(APP_DIR) or not os.path.isdir(APP_DIR):
            os.makedirs(APP_DIR)

        # create credentials.json if it does not exist
        if not os.path.exists(FILE_NAME):
            f = open(FILE_NAME, 'a')
            f.close()





