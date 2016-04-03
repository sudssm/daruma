import os
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_random_name
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]
master_key = generate_key()
manifest_name = generate_random_name()


def setup_function(function):
    for provider in providers:
        provider.wipe()


def test_init():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    assert len(FM.ls("")) == 0


def test_roundtrip():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    assert FM.ls("") == [{"name": "test", "is_directory": False, "size": 4}]
    assert FM.get("test") == "data"


def test_ls_file():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    assert FM.ls("test") == [{"name": "test", "is_directory": False, "size": 4}]


def test_ls_subdirectory():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    target_location = os.path.join("dir", "test")
    FM.put(target_location, "data")
    assert FM.ls("dir") == [{"name": "test", "is_directory": False, "size": 4}]


def test_get_nonexistent():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    with pytest.raises(exceptions.FileNotFound):
        FM.get("blah")


def test_delete():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        FM.get("test")


def test_mk_dir():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.mk_dir("foo/bar")
    assert FM.ls("") == [{"name": "foo", "is_directory": True}]
    assert FM.ls("foo") == [{"name": "bar", "is_directory": True}]


def test_nested_file():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("foo/bar/hi", "data")
    assert FM.ls("") == [{"name": "foo", "is_directory": True}]
    assert FM.ls("foo") == [{"name": "bar", "is_directory": True}]
    assert FM.ls("foo/bar") == [{"name": "hi", "is_directory": False, "size": 4}]
    assert FM.get("foo/bar/hi") == "data"


def test_update():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test", "newdata")
    assert FM.get("test") == "newdata"


def test_update_deletes_old_file():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    old_file_code_name = FM.manifest.get("test").code_name

    FM.put("test", "newdata")
    new_file_code_name = FM.manifest.get("test").code_name

    assert new_file_code_name != old_file_code_name
    for provider in providers:
        with pytest.raises(exceptions.ProviderOperationFailure):
            provider.get(old_file_code_name)


def test_wrong_master_key():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, 3, generate_key(), manifest_name)
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_wrong_manifest_name():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, 3, master_key, generate_random_name())
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_multiple_sessions():
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test2", "moredata")
    assert sorted(FM.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]

    FM = FileManager(providers, 3, master_key, manifest_name)
    FM.load_manifest()
    assert sorted(FM.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]
    assert FM.get("test") == "data"
    assert FM.get("test2") == "moredata"


def test_corrupt_recover():
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
    FM = FileManager(providers, 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    try:
        FM = FileManager(providers, 3, master_key, manifest_name)
        FM.load_manifest()
        FM.ls("")
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3
