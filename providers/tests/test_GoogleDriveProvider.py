from providers.GoogleDriveProvider import GoogleDriveProvider
from custom_exceptions import exceptions
import pytest


def test_wipe():
    FS = GoogleDriveProvider()
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()

    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file2")


def test_roundtrip():
    FS = GoogleDriveProvider()
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = GoogleDriveProvider()
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = GoogleDriveProvider()
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = GoogleDriveProvider()
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = GoogleDriveProvider()
    FS.wipe()
    FS.put("file1", "abc")
    FS = GoogleDriveProvider()
    assert FS.get("file1") == "abc"
