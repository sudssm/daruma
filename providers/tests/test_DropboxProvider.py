from providers.DropboxProvider import DropboxProvider
from custom_exceptions import exceptions
import pytest

ACCESS_TOKEN = "oosk9iu5HYAAAAAAAAAAFjVE1V1dYf_hao8QonpiwtyEoBhn1KMinIuwKHQ9fz8l"


def test_wipe():
    FS = DropboxProvider(ACCESS_TOKEN)
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()

    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file2")


def test_roundtrip():
    FS = DropboxProvider(ACCESS_TOKEN)
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = DropboxProvider(ACCESS_TOKEN)
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = DropboxProvider(ACCESS_TOKEN)
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = DropboxProvider(ACCESS_TOKEN)
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = DropboxProvider(ACCESS_TOKEN)
    FS.wipe()
    FS.put("file1", "abc")
    FS = DropboxProvider(ACCESS_TOKEN)
    assert FS.get("file1") == "abc"
