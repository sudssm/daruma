import os
from appdirs import *
from providers.CredentialManager import CredentialManager
from providers.DropboxProvider import DropboxProvider as provider


APP_NAME = "Trust No One"
APP_DIR = user_config_dir(APP_NAME)
FILE_NAME = os.path.join(user_config_dir(APP_DIR), "credentials.json")


def test_no_directory():
	try:
		if os.path.exists(FILE_NAME):
			os.remove(FILE_NAME)
		credential = CredentialManager.get_credentials(provider)
		assert credential == None
	except:
		assert False


def test_clear_credential():
	CredentialManager.update_credentials(provider, "old credential")
	CredentialManager.update_credentials(provider, "new credential")
	CredentialManager.clear_credentials()
	credential = CredentialManager.get_credentials(provider)
	assert credential == None


def test_get_non_existing_provider():
	CredentialManager.clear_credentials()
	credential = CredentialManager.get_credentials(provider)
	assert credential == None


def test_get_credential():
	CredentialManager.update_credentials(provider, "new credential")
	credential = CredentialManager.get_credentials(provider)
	assert credential == "new credential"


def test_update_credential():
	CredentialManager.update_credentials(provider, "old credential")
	CredentialManager.update_credentials(provider, "new credential")
	credential = CredentialManager.get_credentials(provider)
	assert credential == "new credential"