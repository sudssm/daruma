import ops.exceptions
import ops.manifest
import nacl.utils
import nacl.secret
import copy
import pytest

# Manifest tests


def test_empty_ls():
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content="")


def test_standard_ls():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    manifest = ""
    entries = []

    attributes = {"true_name": "clark_kent.txt", "random_name": "abcdefg", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "superman.pdf", "random_name": "hijklmn", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    manifest = ops.manifest.Manifest(lines=entries)

    assert manifest.ls() == ["clark_kent.txt", "superman.pdf"]


def test_manifest_from_list():
    pass


def test_manifest_from_content():
    pass


def test_manifest_from_both():
    pass


def test_manifest_from_neither():
    pass


def test_manifest_from_list_empty():
    pass


def test_manifest_from_content_empty():
    pass


def test_manifest_stringify():
    pass


def test_standard_get_line():
    pass


def test_missing_get_line():
    pass


# ManifestEntry tests

def test_manifest_line():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    attributes = {"true_name": "clark_kent.txt", "random_name": "abcde", "size": 25, "aes_key": key}
    manifest = ops.manifest.ManifestEntry(attributes=attributes)
    assert "clark_kent.txt,abcde,25," + key == manifest.stringify()


def test_entry_from_string():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    str_entry = "clark_kent.txt,abcde,10," + key
    entry = ops.manifest.ManifestEntry(str_line=str_entry)
    assert entry.attributes == {"true_name": "clark_kent.txt", "random_name": "abcde",
                                "size": 10, "aes_key": key}


def test_entry_from_attributes():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    attrs = {"true_name": "clark_kent", "random_name": "abcde",
             "size": 10, "aes_key": key}
    entry = ops.manifest.ManifestEntry(attributes=attrs)
    assert entry.attributes == attrs


def test_entry_from_both():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    str_entry = "clark_kent.txt,abcde,10," + key
    attrs = {"true_name": "clark_kent", "random_name": "abcde",
             "size": 10, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(str_line=str_entry, attributes=attrs)


def test_entry_from_neither():
    pass


def test_entry_from_invalid_string():
    pass


def test_entry_from_invalid_attributes():
    pass


def test_entry_stringify():
    pass


def test_standard_entry_parse():
    pass


def test_invalid_entry_parse():
    pass


def test_replace_manifest_update():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    manifest = ""
    attributes = []
    entries = []

    attributes.append({"true_name": "clark_kent.txt", "random_name": "abcde", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "superman.pdf", "random_name": "fu75k", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "wonderwoman.ext", "random_name": "k86tj", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "batman.doc", "random_name": "12t45", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "if3685.tioy4et", "random_name": "6h7k9", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    old_random_name = manifest.update_manifest("superman.pdf", "snafu", 52, new_key)  # TODO: assumes we do not rotate keys
    superman = manifest.remove_line("superman.pdf")
    old_manifest.remove_line("superman.pdf")

    assert old_random_name == "fu75k" and manifest == old_manifest and \
        superman.attributes["random_name"] == "snafu" and superman.attributes["size"] == 52


def test_create_manifest_update():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    manifest = ""
    attributes = []
    entries = []

    attributes.append({"true_name": "clark_kent.txt", "random_name": "abcde", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "superman.pdf", "random_name": "fu75k", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "wonderwoman.ext", "random_name": "k86tj", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "batman.doc", "random_name": "12t45", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "if3685.tioy4et", "random_name": "6h7k9", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    # TODO: assumes we do not rotate keys
    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    old_random_name = manifest.update_manifest("diana.pdf", "fubar", 52, new_key)
    diana = manifest.remove_line("diana.pdf")

    assert old_random_name is None and old_manifest == manifest and \
        diana.attributes["random_name"] == "fubar" and diana.attributes["size"] == 52
