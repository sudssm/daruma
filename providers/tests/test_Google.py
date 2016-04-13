from providers.GoogleDriveProvider import GoogleDriveProvider
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions
import pytest
import os

cm = CredentialManager()
cm.load()


def test_wipe():

    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()

    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file2")


def test_roundtrip():
    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    FS.wipe()
    FS.put("file1", "abc")
    FS = GoogleDriveProvider.load_cached_providers(cm)[0][0]
    assert FS.get("file1") == "abc"
