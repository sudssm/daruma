from managers.FileManager import FileManager
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_random_name
import os
import pytest

cm = CredentialManager()
cm.load()


def make_local(cm, path):
    provider = LocalFilesystemProvider(cm)
    provider.connect(path)
    return provider

providers = [make_local(cm, "tmp/" + str(i)) for i in xrange(5)]

master_key = generate_key()
manifest_name = generate_random_name()


def teardown_function(function):
    cm.clear_user_credentials()


def setup_function(function):
    for provider in providers:
        provider.wipe()


def test_init():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    assert len(FM.ls("")) == 0


def test_roundtrip():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    assert FM.ls("") == [{"name": "test", "is_directory": False, "size": 4}]
    assert FM.get("test") == "data"


def test_ls_file():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    assert FM.ls("test") == [{"name": "test", "is_directory": False, "size": 4}]


def test_ls_subdirectory():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    target_location = os.path.join("dir", "test")
    FM.put(target_location, "data")
    assert FM.ls("dir") == [{"name": "test", "is_directory": False, "size": 4}]


def test_get_nonexistent():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    with pytest.raises(exceptions.FileNotFound):
        FM.get("blah")


def test_delete():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        FM.get("test")


def test_mk_dir():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.mk_dir("foo/bar")
    assert FM.ls("") == [{"name": "foo", "is_directory": True}]
    assert FM.ls("foo") == [{"name": "bar", "is_directory": True}]


def test_delete_directory():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.mk_dir("foo")
    FM.delete("foo")
    assert FM.ls("") == []


def test_nested_file():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("foo/bar/hi", "data")
    assert FM.ls("") == [{"name": "foo", "is_directory": True}]
    assert FM.ls("foo") == [{"name": "bar", "is_directory": True}]
    assert FM.ls("foo/bar") == [{"name": "hi", "is_directory": False, "size": 4}]
    assert FM.get("foo/bar/hi") == "data"


def test_update():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test", "newdata")
    assert FM.get("test") == "newdata"


def test_update_deletes_old_file():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
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
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, len(providers), 3, generate_key(), manifest_name)
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_wrong_manifest_name():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM = FileManager(providers, len(providers), 3, master_key, generate_random_name())
    with pytest.raises(exceptions.FatalOperationFailure):
        FM.load_manifest()


def test_multiple_sessions():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test2", "moredata")
    assert sorted(FM.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]

    FM = FileManager(providers, len(providers), 3, master_key, manifest_name)
    FM.load_manifest()
    assert sorted(FM.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]
    assert FM.get("test") == "data"
    assert FM.get("test2") == "moredata"


def test_corrupt_recover():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    FM = FileManager(providers, len(providers), 3, master_key, manifest_name)
    with pytest.raises(exceptions.OperationFailure):
        FM.load_manifest()

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FM.load_manifest()
    assert len(excinfo.value.failures) == 2


def test_corrupt_fail():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    with pytest.raises(exceptions.FatalOperationFailure) as excinfo:
        FM.load_manifest()
    assert len(excinfo.value.failures) == 3


def test_change_k():
    FM = FileManager(providers, len(providers), 4, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test2", "data2")

    FM.file_reconstruction_threshold = 3
    FM.reset()

    FM.load_manifest()
    assert FM.get("test") == "data"
    assert FM.get("test2") == "data2"

    # check that we are using new k
    providers[0].wipe()
    providers[1].wipe()
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FM.get("test")
    assert excinfo.value.result == "data"


def test_add_provider():
    FM = FileManager(providers[0:4], 4,  3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test2", "data2")

    FM.providers.append(providers[-1])
    FM.reset()

    FM.load_manifest()
    assert FM.get("test") == "data"
    assert FM.get("test2") == "data2"

    # check that we are resilient
    providers[0].wipe()
    providers[1].wipe()
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FM.get("test")
    assert excinfo.value.result == "data"


def test_remove_provider_and_decrement_k():
    FM = FileManager(providers, 5, 4, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("test", "data")
    FM.put("test2", "data2")

    FM.file_reconstruction_threshold = 3
    FM.providers.remove(providers[-1])
    FM.reset()

    FM.load_manifest()
    assert FM.get("test") == "data"
    assert FM.get("test2") == "data2"

    # check that we are using new k
    providers[0].wipe()
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FM.get("test")
    assert excinfo.value.result == "data"


def test_get_directory():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.mk_dir("dir1")

    with pytest.raises(exceptions.FileNotFound):
        FM.get("dir1")


def test_path_generator():
    FM = FileManager(providers, len(providers), 3, master_key, manifest_name, setup=True)
    FM.load_manifest()

    FM.put("file1", "data1")
    FM.put("file2", "data2")
    FM.put("dir1/file3", "data3")
    FM.mk_dir("dir1/dir2")

    expected_paths = ["file1", "file2", "dir1", "dir1/file3", "dir1/dir2"]

    assert sorted(FM.path_generator()) == sorted(expected_paths)
