import json
import os
from tools.utils import APP_NAME
from appdirs import user_config_dir
from collections import defaultdict
from pkg_resources import resource_stream
from copy import deepcopy


class CredentialManager:
    """
    A key-value store backed by JSON files to store user and app credentials
    """
    def __init__(self):
        """
        Initialize a credential manager. The user must call load() before using the object
        """
        # get the directory of the providers module
        self.config_dir = user_config_dir(APP_NAME)
        self.user_creds_file = os.path.join(self.config_dir, "user_credentials.json")
        self.app_creds_file = "app_credentials.json"

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
        try:
            app_creds_stream = resource_stream(__name__, self.app_creds_file)
            self.app_creds = json.load(app_creds_stream)
            app_creds_stream.close()
        except (IOError, ValueError):
            raise ValueError("Application credentials file could not be loaded")

    def _load_user_creds(self):
        """
        Attempts to load user credentials json file
        Creates an empty credentials file if unable to read or parse
        """
        try:
            with open(self.user_creds_file, 'r') as file:
                creds = json.load(file)
                self.user_creds = defaultdict(dict, creds)
        except (IOError, ValueError):
            self.user_creds = defaultdict(dict)
            self._write_user_creds()

    def _write_user_creds(self):
        """
        Write user credentials to the backing file.
        Raises IOError on write errors
        """
        # create the folder if it doesn't exist
        try:
            os.makedirs(self.config_dir)
        except OSError:
            pass
        with open(self.user_creds_file, 'w') as file:
            json.dump(self.user_creds, file)

    def get_user_credentials(self, provider_class):
        """
        Get all user credentials for a provider type
        Args:
            provider_class: a provider class
        Returns:
            The credentials for the specified provider, or [] if unavailable
            credentials is a dictionary of provider_identifier to credential values that have been stored in this manager
        """
        return deepcopy(self.user_creds[provider_class.provider_identifier()])

    def get_app_credentials(self, provider_class):
        """
        Get app credentials for a provider
        Args:
            provider_class: a provider class
        Returns:
            The credentials for the specified provider, or None if unavailable
        """
        return self.app_creds.get(provider_class.provider_identifier())

    def set_user_credentials(self, provider_class, account_identifier, credentials):
        """
        Update user credential for the provider
        Args:
            provider_class: a provider class
            account_identifier: a value unique across all providers of this type
                                 for identification (e.g. username)
            credentials: a JSON-ifyable dictionary or string to store
        """
        self.user_creds[provider_class.provider_identifier()][account_identifier] = credentials
        self._write_user_creds()

    def clear_user_credentials(self, provider_class=None, account_identifier=None):
        """
        Remove the stored credential for the specific instance of provider_class, provider_identifier
        If provider_identifier is None, all credentials for the provider_class will be deleted
        If provider_class is None, all credentials for all providers will be wiped
        Args:
            provider_class: a provider class
            account_identifier: a value unique across all providers of this type
                                 for identification (e.g. username)
        """
        try:
            if provider_class is None:
                self.user_creds = defaultdict(dict)
            elif account_identifier is None:
                del self.user_creds[provider_class.provider_identifier()]
            else:
                del self.user_creds[provider_class.provider_identifier()][account_identifier]
            self._write_user_creds()
        except KeyError:
            return
