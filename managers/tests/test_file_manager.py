from managers.FileManager import FileManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_random_name
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]
master_key = generate_key()
manifest_name = generate_random_name()


def test_init():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    assert len(FM.ls()) == 0


def test_roundtrip():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    assert FM.ls() == ["test"]
    assert FM.get("test") == "data"


def test_get_nonexistent():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    with pytest.raises(exceptions.FileNotFound):
        FM.get("blah")


def test_delete():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    FM.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        FM.get("test")


def test_update():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    FM.put("test", "newdata")
    assert FM.get("test") == "newdata"


def test_wrong_master_key():
    for provider in providers:
        provider.wipe()
    FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, 3, generate_key(), manifest_name)
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_wrong_manifest_name():
    for provider in providers:
        provider.wipe()
    FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, 3, master_key, generate_random_name())
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_multiple_sessions():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    FM.put("test2", "moredata")
    assert sorted(FM.ls()) == ["test", "test2"]

    FM = FileManager(providers, 3, master_key, manifest_name)
    FM.load_manifest()
    assert sorted(FM.ls()) == ["test", "test2"]
    assert FM.get("test") == "data"
    assert FM.get("test2") == "moredata"


def test_corrupt_recover():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    FM = FileManager(providers, 3, master_key, manifest_name)
    with pytest.raises(exceptions.OperationFailure):
        FM.load_manifest()

    try:
        FM.get("test")
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 2


def test_corrupt_fail():
    for provider in providers:
            provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()
    FM.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    try:
        FM = FileManager(providers, 3, master_key, manifest_name)
        FM.load_manifest()
        FM.ls()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3
