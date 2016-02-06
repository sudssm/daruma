from managers.FileManager import FileManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools import gen
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]
master_key = gen.generate_key()
manifest_name = gen.generate_name()


def test_init():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    assert len(FM.ls()) == 0


def test_roundtrip():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    assert FM.ls() == ["test"]
    assert FM.get("test") == "data"


def test_get_nonexistent():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    with pytest.raises(exceptions.FileNotFound):
        FM.get("blah")


def test_delete():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    FM.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        FM.get("test")


def test_update():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    FM.put("test", "newdata")
    assert FM.get("test") == "newdata"


def test_wrong_master_key():
    for provider in providers:
        provider.wipe()
    FileManager(providers, 3, master_key, manifest_name, setup=True)
    with pytest.raises(exceptions.ManifestGetError):
        FM = FileManager(providers, 3, gen.generate_key(), manifest_name)
        FM.ls()


def test_wrong_manifest_name():
    for provider in providers:
        provider.wipe()
    FileManager(providers, 3, master_key, manifest_name, setup=True)
    with pytest.raises(exceptions.ManifestGetError):
        FM = FileManager(providers, 3, master_key, gen.generate_name())
        FM.ls()


def test_multiple_sessions():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    FM.put("test2", "moredata")
    assert sorted(FM.ls()) == ["test", "test2"]

    FM = FileManager(providers, 3, master_key, manifest_name)
    assert sorted(FM.ls()) == ["test", "test2"]
    assert FM.get("test") == "data"
    assert FM.get("test2") == "moredata"


def test_corrupt_recover():
    for provider in providers:
        provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    FM = FileManager(providers, 3, master_key, manifest_name)
    assert FM.get("test") == "data"


def test_corrupt_fail():
    for provider in providers:
            provider.wipe()
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    with pytest.raises(exceptions.ManifestGetError):
        FM = FileManager(providers, 3, master_key, manifest_name)
        FM.ls()
