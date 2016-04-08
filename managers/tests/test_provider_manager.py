from managers.ProviderManager import ProviderManager
from managers.CredentialManager import CredentialManager
from providers.LocalFilesystemProvider import LocalFilesystemProvider


cm = CredentialManager()


def setup_function(function):
    cm.clear_user_credentials()
    cm.load()


def teardown_function(function):
    cm.clear_user_credentials()


def test_load_providers():
    # put a new provider in the credentials
    fs = LocalFilesystemProvider(cm, "foo")

    pm = ProviderManager()
    cached_providers, errors = pm.load_all_providers_from_credentials()

    assert map(lambda provider: provider.uuid, cached_providers) == [fs.uuid]

