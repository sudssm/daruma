import json
from appdirs import *

APP_NAME = "Trust No One"
FILE_NAME = user_config_dir(APP_NAME) + "config.json"
CREDENTIAL_FILE = open(FILE_NAME, 'rw+')

class CredentialManager(object):

	@staticmethod
	def get_credentials(provider):
		"""
        Get user credentials for a provider. Return None if noe presented

        Args:
            provider: a provider class
        """
		# load user credentials 
		try:
			credentials = json.load(CREDENTIAL_FILE)
		except ValueError:
			credentials = {}

		return credentials.get(provider.__class__)


	@staticmethod
	def update_credentials(provider, credentials):
		try:
			credentials = json.load(CREDENTIAL_FILE)
		except ValueError:
			credentials = {}

		credentials[provider.__class__] = credentials

		json.dump(credentials, CREDENTIAL_FILE)
