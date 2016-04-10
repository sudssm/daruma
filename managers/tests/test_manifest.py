from custom_exceptions import exceptions
from tools.encryption import generate_key
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
from managers.manifest import *
import pytest

codename1 = "ABCDEABCDEABCDEABCDEABCDEABCDEAB"
codename2 = "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQHI"
codename3 = "K86TJK86TJK86TJK86TJK86TJK86TJK8"
codename4 = "12T4512T4512T4512T4512T4512T4512"
codename5 = "6H7K96H7K96H7K96H7K96H7K96H7K96H"
codename6 = "SNAFUSNAFUSNAFUSNAFUSNAFUSNAFUSN"


def test_empty_manifest_equals():
    manifest1 = Manifest()
    manifest2 = Manifest()

    assert manifest1 == manifest2


def test_interesting_manifest_equals():
    key1 = generate_key()
    key2 = generate_key()
    key3 = generate_key()
    key4 = generate_key()

    manifest1 = Manifest()
    manifest1.update_file(os.path.join("dir1", "CLARK_KENT.TXT"), codename1, 34, key1)
    manifest1.update_file(os.path.join("dir1", "dir2", "KAL_EL.xls"), codename2, 42, key2)
    manifest1.update_file("SUPERMAN.PDF", codename3, 32, key3)
    manifest1.update_file("MAN_OF_STEEL.JPG", codename4, 23, key4)

    manifest2 = Manifest()
    manifest2.update_file(os.path.join("dir1", "CLARK_KENT.TXT"), codename1, 34, key1)
    manifest2.update_file(os.path.join("dir1", "dir2", "KAL_EL.xls"), codename2, 42, key2)
    manifest2.update_file("SUPERMAN.PDF", codename3, 32, key3)
    manifest2.update_file("MAN_OF_STEEL.JPG", codename4, 23, key4)

    assert manifest1 == manifest2


def test_interesting_manifest_nequals():
    key1 = generate_key()
    key2 = generate_key()
    key3 = generate_key()
    key4 = generate_key()

    manifest1 = Manifest()
    manifest1.update_file(os.path.join("dir1", "CLARK_KENT.TXT"), codename1, 34, key1)
    manifest1.update_file(os.path.join("dir1", "dir2", "KAL_EL.xls"), codename2, 42, key2)
    manifest1.update_file("SUPERMAN.PDF", codename3, 32, key3)
    manifest1.update_file("MAN_OF_STEEL.JPG", codename4, 23, key4)

    manifest2 = Manifest()
    manifest2.update_file(os.path.join("dir1", "CLARK_KENT.TXT"), codename1, 34, key1)
    manifest2.update_file(os.path.join("dir1", "dir2", "KAL_EL.xls"), codename2, 42, key2)
    manifest2.update_file("SUPERMAN.PDF", codename3, 32, key3)
    manifest2.update_file("MAN_OF_STEEL.JPG", codename4, 24, key4)  # Size is different

    assert manifest1 != manifest2


def test_empty_serialization():
    manifest = Manifest()
    manifest_string = manifest.serialize()

    reconstructed_manifest = Manifest.deserialize(manifest_string)
    assert manifest == reconstructed_manifest


def test_interesting_serialization():
    manifest = Manifest()
    manifest.update_file(os.path.join("dir1", "CLARK_KENT.TXT"), codename1, 34, generate_key())
    manifest.update_file(os.path.join("dir1", "dir2", "KAL_EL.xls"), codename2, 42, generate_key())
    manifest.update_file("SUPERMAN.PDF", codename3, 32, generate_key())
    manifest.update_file("MAN_OF_STEEL.JPG", codename4, 23, generate_key())
    manifest_string = manifest.serialize()

    reconstructed_manifest = Manifest.deserialize(manifest_string)
    assert manifest == reconstructed_manifest


def test_get_file_info():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    target_location = os.path.join("dir", test_attributes["name"])
    expected_node = File.from_values(**test_attributes)

    manifest = Manifest()
    manifest.update_file(target_location, test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    get_results = manifest.get(target_location)
    assert get_results == expected_node


def test_get_file_codename():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}

    manifest = Manifest()
    manifest.update_file(test_attributes["name"], test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    get_results = manifest.get(test_attributes["name"])
    assert get_results.code_name == test_attributes["code_name"]


def test_get_file_size():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}

    manifest = Manifest()
    manifest.update_file(test_attributes["name"], test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    get_results = manifest.get(test_attributes["name"])
    assert get_results.size == test_attributes["size"]


def test_get_file_key():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}

    manifest = Manifest()
    manifest.update_file(test_attributes["name"], test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    get_results = manifest.get(test_attributes["name"])
    assert get_results.key == test_attributes["key"]


def test_get_on_directory():
    expected_node = Directory.from_values("dir1")

    manifest = Manifest()
    manifest.create_directory("dir1")

    get_results = manifest.get("dir1")
    assert get_results == expected_node


def test_get_root():
    expected_node = Directory.from_values("")

    manifest = Manifest()

    get_results = manifest.get("")
    assert get_results == expected_node


def test_get_nonexistent_path():
    manifest = Manifest()

    with pytest.raises(exceptions.InvalidPath):
        manifest.get("asdf")


def test_get_malformed_path():
    manifest = Manifest()
    manifest.update_file("dir", codename1, 34, generate_key())

    with pytest.raises(exceptions.InvalidPath):
        manifest.get(os.path.join("dir", "CLARK_KENT.TXT"))


def test_remove_file():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    target_location = os.path.join("dir", test_attributes["name"])
    expected_node = File.from_values(**test_attributes)

    manifest = Manifest()
    manifest.update_file(target_location, test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    remove_results = manifest.remove(target_location)
    assert remove_results == expected_node

    result_children = manifest.get("dir").get_children()
    assert result_children == []

    with pytest.raises(exceptions.InvalidPath):
        manifest.get(target_location)


def test_remove_directory():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    target_location = os.path.join("dir", test_attributes["name"])

    manifest = Manifest()
    manifest.update_file(target_location, test_attributes["code_name"], test_attributes["size"], test_attributes["key"])
    expected_node = manifest.get("dir")

    remove_results = manifest.remove("dir")
    assert remove_results == expected_node

    result_children = manifest.get("").get_children()
    assert result_children == []


def test_remove_invalid():
    manifest = Manifest()

    with pytest.raises(exceptions.InvalidPath):
        manifest.remove("asdfas")


def test_remove_invalid_parent_is_file():
    manifest = Manifest()
    manifest.update_file("CLARK_KENT", codename1, 34, generate_key())

    with pytest.raises(exceptions.InvalidPath):
        manifest.remove(os.path.join("CLARK_KENT", "asfasdfa"))


def test_remove_root():
    manifest = Manifest()

    with pytest.raises(exceptions.InvalidPath):
        manifest.remove("")


def test_update_new_file():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    expected_node = File.from_values(**test_attributes)

    manifest = Manifest()
    old_code_name = manifest.update_file(test_attributes["name"], test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    assert old_code_name is None

    get_results = manifest.get(test_attributes["name"])
    assert get_results == expected_node


def test_update_overwrite_file():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    replacement_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename2, "size": 23, "key": generate_key()}
    expected_old_node = File.from_values(**test_attributes)
    expected_replacement_node = File.from_values(**replacement_attributes)

    manifest = Manifest()
    manifest.update_file(test_attributes["name"], test_attributes["code_name"], test_attributes["size"], test_attributes["key"])
    old_file = manifest.update_file(replacement_attributes["name"], replacement_attributes["code_name"], replacement_attributes["size"], replacement_attributes["key"])

    assert old_file == expected_old_node

    get_results = manifest.get(replacement_attributes["name"])
    assert get_results == expected_replacement_node


def test_update_overwrite_file_in_directory():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    replacement_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename2, "size": 23, "key": generate_key()}
    target_location = os.path.join("dir", test_attributes["name"])
    expected_node = File.from_values(**replacement_attributes)

    manifest = Manifest()
    manifest.update_file(target_location, test_attributes["code_name"], test_attributes["size"], test_attributes["key"])
    manifest.update_file(target_location, replacement_attributes["code_name"], replacement_attributes["size"], replacement_attributes["key"])

    get_results = manifest.get(target_location)
    assert get_results == expected_node


def test_update_root():
    manifest = Manifest()

    with pytest.raises(exceptions.InvalidPath):
        manifest.update_file("", codename1, 32, generate_key())


def test_update_directory():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    expected_node = File.from_values(**test_attributes)

    manifest = Manifest()
    target_location = os.path.join("dir", test_attributes["name"])
    manifest.update_file(target_location, test_attributes["code_name"], test_attributes["size"], test_attributes["key"])

    with pytest.raises(exceptions.InvalidPath):
        manifest.update_file("dir", codename2, 34, generate_key())

    # Test that the manifest hasn't been modified
    get_results = manifest.get(target_location)
    assert get_results == expected_node


def test_update_bad_path():
    manifest = Manifest()
    manifest.update_file("dir", codename1, 34, generate_key())

    with pytest.raises(exceptions.InvalidPath):
        manifest.update_file(os.path.join("dir", "CLARK_KENT.TXT"), codename2, 53, generate_key())


def test_mkdir_root():
    expected_node = Directory.from_values("")

    manifest = Manifest()
    manifest.create_directory("")

    get_results = manifest.get("")
    assert get_results == expected_node


def test_mkdir_at_root():
    expected_node = Directory.from_values("dir")

    manifest = Manifest()
    manifest.create_directory("dir")

    get_results = manifest.get("dir")
    assert get_results == expected_node


def test_move_in_root():
    manifest = Manifest()
    manifest.update_file("file", codename1, 3, generate_key())
    node = manifest.get("file")
    manifest.move("file", "new_file")

    assert node == manifest.get("new_file")
    with pytest.raises(exceptions.InvalidPath):
        manifest.get("file")


def test_move_file():
    manifest = Manifest()
    manifest.update_file("dir/file", codename1, 3, generate_key())
    node = manifest.get("dir/file")
    manifest.move("dir/file", "dir/new_file")

    assert node == manifest.get("dir/new_file")
    with pytest.raises(exceptions.InvalidPath):
        manifest.get("dir/file")


def test_move_folder():
    manifest = Manifest()
    manifest.create_directory("dir")
    node = manifest.get("dir")
    manifest.move("dir", "new_dir")

    assert node == manifest.get("new_dir")
    with pytest.raises(exceptions.InvalidPath):
        manifest.get("dir")


def test_move_to_existing():
    manifest = Manifest()
    manifest.update_file("file", codename1, 3, generate_key())
    manifest.update_file("new_file", codename1, 3, generate_key())
    node = manifest.get("file")

    with pytest.raises(exceptions.InvalidPath):
        manifest.move("file", "new_file")


def test_move_from_invalid():
    manifest = Manifest()
    with pytest.raises(exceptions.InvalidPath):
        manifest.move("file", "new_file")


def test_nested_move():
    manifest = Manifest()
    manifest.create_directory("bar")
    manifest.update_file("foo/file", codename1, 3, generate_key())
    node = manifest.get("foo")
    manifest.move("foo", "bar/foo2")

    assert node == manifest.get("bar/foo2")
    with pytest.raises(exceptions.InvalidPath):
        manifest.get("foo")


def test_move_into_self():
    manifest = Manifest()
    manifest.update_file("foo/file", codename1, 3, generate_key())
    node = manifest.get("foo")
    manifest.move("foo", "foo/foo")

    assert node == manifest.get("foo/foo")


def test_mkdir_subdirectory():
    test_attributes = {"name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "key": generate_key()}
    expected_file = File.from_values(**test_attributes)
    expected_dir2 = Directory.from_values("dir2")
    expected_dir = Directory.from_values("dir", [expected_file, expected_dir2])
    expected_root = Directory.from_values("", [expected_dir])

    manifest = Manifest()
    manifest.update_file(os.path.join("dir", test_attributes["name"]), test_attributes["code_name"], test_attributes["size"], test_attributes["key"])
    manifest.create_directory(os.path.join("dir", "dir2"))

    root = manifest.get("")
    assert root == expected_root


def test_mkdir_over_existing():
    manifest = Manifest()
    manifest.update_file(os.path.join("dir", "CLARK_KENT.TXT"), codename1, 23, generate_key())
    expected_root = manifest.get("")

    manifest.create_directory("dir")

    root = manifest.get("")
    assert root == expected_root


def test_mkdir_with_conflicting_file():
    manifest = Manifest()
    manifest.update_file("dir", codename1, 23, generate_key())

    with pytest.raises(exceptions.InvalidPath):
        manifest.create_directory("dir")


def test_generate_files_empty():
    manifest = Manifest()

    assert list(manifest.generate_files_under("")) == []


def test_generate_files_tree():
    key1 = generate_key()

    manifest = Manifest()

    expected_files = [
        File.from_values("bar", codename1, 23, key1),
        File.from_values("asdf", codename1, 23, key1),
    ]
    created_filepaths = ["foo", "asd", "dir1/bar", "dir1/dir2/asdf", "dir3/baz"]

    for path in created_filepaths:
        manifest.update_file(path, codename1, 23, key1)

    assert sorted(manifest.generate_files_under("dir1")) == sorted(expected_files)


def test_roundtrip_providers():
    cm = CredentialManager()
    cm.load()

    def make_local(cm, path):
        provider = LocalFilesystemProvider(cm)
        provider.connect(path)
        return provider

    providers = [make_local(cm, "tmp/" + str(i)) for i in xrange(5)]

    manifest = Manifest()
    manifest.set_providers(providers)

    provider_strings = map(lambda provider: provider.uuid, providers)

    assert Manifest.deserialize(manifest.serialize()).get_provider_strings() == provider_strings
