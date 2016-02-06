from providers.LocalFilesystemProvider import LocalFilesystemProvider
from providers.BaseProvider import BaseProvider
from custom_exceptions import exceptions
import pytest
import os


def test_wipe():
    FS = LocalFilesystemProvider("tmp")
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()

    assert len(os.listdir("tmp/" + BaseProvider.ROOT_DIR)) == 0


def test_roundtrip():
    FS = LocalFilesystemProvider("tmp")
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = LocalFilesystemProvider("tmp")
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = LocalFilesystemProvider("tmp")
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = LocalFilesystemProvider("tmp")
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = LocalFilesystemProvider("tmp")
    FS.wipe()
    FS.put("file1", "abc")
    FS = LocalFilesystemProvider("tmp")
    assert FS.get("file1") == "abc"
