from managers.FileManager import FileManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from crypto.encryption import generate_key
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]
master_key = generate_key()


def test_init():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    assert len(FM.ls()) == 0


def test_roundtrip():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    assert FM.ls() == ["test"]
    assert FM.get("test") == "data"


def test_get_nonexistent():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    assert FM.get("blah") is None


def test_delete():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    FM.delete("test")
    assert FM.get("test") is None


def test_update():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    FM.put("test", "newdata")
    assert FM.get("test") == "newdata"


def test_wrong_master_key():
    for provider in providers:
        provider.wipe()
    FileManager(providers, 3, master_key)
    with pytest.raises(exceptions.DecryptError):
        FileManager(providers, 3, generate_key())


def test_multiple_sessions():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    FM.put("test2", "moredata")
    assert sorted(FM.ls()) == ["test", "test2"]

    FM = FileManager(providers, 3, master_key)
    assert sorted(FM.ls()) == ["test", "test2"]
    assert FM.get("test") == "data"
    assert FM.get("test2") == "moredata"


def test_corrupt_recover():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    FM = FileManager(providers, 3, master_key)
    assert FM.get("test") == "data"


def test_corrupt_fail():
    for provider in providers:
            provider.wipe()
    FM = FileManager(providers, 3, master_key)
    FM.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    with pytest.raises(exceptions.DecodeError):
        FM = FileManager(providers, 3, master_key)
