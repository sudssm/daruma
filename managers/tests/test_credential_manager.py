from managers.CredentialManager import CredentialManager
from providers.DropboxProvider import DropboxProvider
from providers.TestProvider import TestProvider
import os
import pytest


def test_user_cred_mising():
    cm = CredentialManager()
    if os.path.exists(cm.user_creds_file):
        os.remove(cm.user_creds_file)

    cm.load()

    assert cm.user_creds == {}


def test_app_cred_missing():
    cm = CredentialManager()
    # To test this, we don't want to remove the example app credential file
    # So we change the file location to an invalid one
    cm.app_creds_file = "foobarfile"

    with pytest.raises(ValueError):
        cm.load()


def test_get_not_exists():
    cm = CredentialManager()
    cm.load()
    cm.clear_user_credentials(DropboxProvider)
    assert cm.get_app_credentials(TestProvider) is None
    assert cm.get_user_credentials(DropboxProvider) == {}


def test_roundtrip_user():
    cm = CredentialManager()
    cm.load()
    foo_creds = {"a": 1}
    bar_creds = "a_string"
    cm.set_user_credentials(DropboxProvider, "foo", foo_creds)
    cm.set_user_credentials(DropboxProvider, "bar", bar_creds)

    cm.load()
    assert cm.get_user_credentials(DropboxProvider) == {"foo": foo_creds, "bar": bar_creds}

    cm.clear_user_credentials(DropboxProvider, "foo")
    cm.load()
    assert cm.get_user_credentials(DropboxProvider) == {"bar": bar_creds}

    cm.clear_user_credentials(DropboxProvider, "bar")

    cm.load()
    assert cm.get_user_credentials(DropboxProvider) == {}


def test_clear_entire_provider():
    cm = CredentialManager()
    cm.load()
    cm.set_user_credentials(DropboxProvider, "foo", 0)
    cm.set_user_credentials(DropboxProvider, "bar", 1)
    cm.clear_user_credentials(DropboxProvider)

    cm.load()
    assert cm.get_user_credentials(DropboxProvider) == {}


def test_get_app_credentials():
    cm = CredentialManager()
    # Assume that the packaging includes an app credential file with at least "Dropbox"
    cm.load()
    assert cm.get_app_credentials(DropboxProvider) is not None
