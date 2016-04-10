from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions
import pytest
import os

cm = CredentialManager()
cm.load()


def teardown_function(function):
    cm.clear_user_credentials()


def test_wipe():
    FS = LocalFilesystemProvider(cm)
    FS.connect("tmp")
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()

    assert len(os.listdir("tmp/" + FS.ROOT_DIR)) == 0


def test_roundtrip():
    FS = LocalFilesystemProvider(cm)
    FS.connect("tmp")
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = LocalFilesystemProvider(cm)
        FS.connect("tmp")
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = LocalFilesystemProvider(cm)
    FS.connect("tmp")
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = LocalFilesystemProvider(cm)
    FS.connect("tmp")
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = LocalFilesystemProvider(cm)
    FS.connect("tmp")
    FS.wipe()
    FS.put("file1", "abc")
    providers, _ = LocalFilesystemProvider.load_cached_providers(cm)
    FS = providers[0]
    assert FS.get("file1") == "abc"
