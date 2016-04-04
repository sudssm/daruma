import json
import os
import providers
from appdirs import *


class CredentialManager:
    """
    A key-value store backed by JSON files to store user and app credentials
    """
    def __init__(self):
        """
        Initialize a credential manager. The user must call load() before using the object
        """
        # get the directory of the providers module
        providers_dir = os.path.dirname(providers.__file__)
        self.config_dir = user_config_dir("daruma")
        self.user_creds_file = os.path.join(self.config_dir, "user_credentials.json")
        self.app_creds_file = os.path.join(providers_dir, "app_credentials.json")

    def load(self):
        """
        Load all credentials. To be called before using the manager.
        Raises ValueError if valid credentials files cannot be loaded
        """
        self._load_app_creds()
        self._load_user_creds()

    def _load_app_creds(self):
        """
        Attempt to load the application credentials json file
        Raises ValueError if the file isn't found or malformed
        """
        # TODO make sure this works when packaged
        try:
            with open(self.app_creds_file, 'r') as file:
                self.app_creds = json.load(file)
        except (IOError, ValueError):
            raise ValueError("Application credentials file could not be loaded")

    def _load_user_creds(self):
        """
        Attempts to load user credentials json file
        Creates an stores empty credentials if unable to read
        """
        try:
            with open(self.user_creds_file, 'r') as file:
                self.user_creds = json.load(file)
        except (IOError, ValueError):
            self.user_creds = {}
            self._write_user_creds()

    def _write_user_creds(self):
        """
        Write user credentials to the backing file.
        Raises IOError on write errors
        """
        # create the folder if it doesn't exist
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
        with open(self.user_creds_file, 'w') as file:
            json.dump(self.user_creds, file)

    def get_user_credentials(self, provider_class):
        """
        Get user credentials for a provider
        Args:
            provider_class: a string representing the provider's class
        Returns:
            The credentials for the specified provider, or None if unavailable
        """
        return self.user_creds.get(provider_class)

    def get_app_credentials(self, provider_class):
        """
        Get app credentials for a provider
        Args:
            provider_class: a string representing the provider's class
        Returns:
            The credentials for the specified provider, or None if unavailable
        """
        return self.app_creds.get(provider_class)

    def set_user_credentials(self, provider_class, credentials):
        """
        Update user credential for the provider
        Args:
            provider_class: a string representing the provider's class
            credentials: a JSON-ifyable dictionary or string to store
        """
        self.user_creds[provider_class] = credentials
        self._write_user_creds()

    def clear_user_credentials(self, provider_class):
        """
        Remove the stored credential for the provider
        Args:
            provider_class: a string representing the provider's class
        """
        if provider_class in self.user_creds:
            del self.user_creds[provider_class]
        self._write_user_creds()
