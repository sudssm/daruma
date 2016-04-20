"""
This is a test file for all OAuth providers
All providers must have cached user credentials
This will not be automatically run via py.test
"""
from providers.DropboxProvider import DropboxProvider
from providers.GoogleDriveProvider import GoogleDriveProvider
from providers.BoxProvider import BoxProvider
from providers.OneDriveProvider import OneDriveProvider
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions
import zlib
import pytest

cm = CredentialManager()
cm.load()
classes = [DropboxProvider, GoogleDriveProvider, BoxProvider, OneDriveProvider]


def test_wipe():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.put("file1", "abc")
        FS.put("file2", "def")
        FS.wipe()

        with pytest.raises(exceptions.ProviderOperationFailure):
            FS.get("file1")
        with pytest.raises(exceptions.ProviderOperationFailure):
            FS.get("file2")


def test_roundtrip():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.put("file1", zlib.compress("abc"))
        assert zlib.decompress(FS.get("file1")) == "abc"


def test_exception_has_provider():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.wipe()
        with pytest.raises(exceptions.ProviderOperationFailure) as excinfo:
            FS.get("file1")
        assert excinfo.value.provider == FS


def test_get_nonexisting():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.wipe()
        with pytest.raises(exceptions.ProviderOperationFailure):
            FS.get("file1")


def test_delete():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.put("file1", "abc")
        FS.delete("file1")
        with pytest.raises(exceptions.ProviderOperationFailure):
            FS.get("file1")


def test_multiple_sessions():
    for cls in classes:
        print cls
        FS = cls.load_cached_providers(cm)[0][0]
        FS.wipe()
        FS.put("file1", "abc")
        FS = cls.load_cached_providers(cm)[0][0]
        assert FS.get("file1") == "abc"
