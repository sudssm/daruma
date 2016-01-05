import ops.exceptions
import ops.manifest
import nacl.utils
import nacl.secret
import copy
import pytest

# Manifest tests


def test_regex_standard():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_start():
    key1 = '\n\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_mid():
    key1 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_end():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_start():
    key1 = ',\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_mid():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>,\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_end():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_no_true():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = ",ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34" + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_no_random():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_no_size():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_no_key():
    key1 = ''
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_random_long():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,ABCDEFGHIJABCDEFGHIJABCDEFGHIJabKLMNOPQRS,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_random_short():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,ABC,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_key_long():
    key1 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xd7k\xb6\xd5\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_key_short():
    key1 = '\xc2\x95\x1b\xbe\x80jb\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_regex_missing_delim():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    content = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34" + key1 + "\n" + \
              "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key2 + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(content=content)


def test_empty_ls():
    empty = ops.manifest.Manifest(content="")
    assert empty.ls() == []


def test_standard_ls_lines():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    manifest = ops.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_standard_ls_content():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_mid_ls_lines():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    manifest = ops.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_end_ls_lines():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    manifest = ops.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_mid_ls_content():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_end_ls_content():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key1}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key2}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_manifest_from_list():
    entries = []
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 45, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    manifest = ops.manifest.Manifest(lines=entries)
    assert manifest.stringify() == "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34," + key + "\n" + \
                                   "SUPERMAN.PDF,HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi,45," + key + "\n"


def test_manifest_from_content():
    entries = []
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    attributes = {"true_name": "FIREFLY.TXT", "code_name": "AD2BC_EF5JAD2BC_EF5JAD2BC_EF5Jad", "size": 34, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SERENITY.PDF", "code_name": "78ILM_OPQ178ILM_OPQ178ILM_OPQ178", "size": 45, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    manifest = ops.manifest.Manifest(content=content)
    assert manifest.stringify() == "FIREFLY.TXT,AD2BC_EF5JAD2BC_EF5JAD2BC_EF5Jad,34," + key + "\n" + \
                                   "SERENITY.PDF,78ILM_OPQ178ILM_OPQ178ILM_OPQ178,45," + key + "\n"


def test_manifest_from_both():
    entries = []
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    attributes = {"true_name": "FIREFLY.TXT", "code_name": "AD2BC_EF5JAD2BC_EF5JAD2BC_EF5Jad", "size": 34, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SERENITY.PDF", "code_name": "78ILM_OPQ178ILM_OPQ178ILM_OPQ178", "size": 45, "aes_key": key}
    entries.append(ops.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += entry.stringify() + "\n"

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.Manifest(lines=entries, content=content)


def test_manifest_from_neither():
    manifest = ops.manifest.Manifest()
    assert manifest.lines == []


def test_manifest_from_list_empty():
    entries = []
    manifest = ops.manifest.Manifest(lines=entries)
    assert manifest.lines == []


def test_manifest_from_content_empty():
    content = ""
    manifest = ops.manifest.Manifest(content=content)
    assert manifest.lines == []


def test_roundtrip_empty():
    content = ""
    manifest = ops.manifest.Manifest(content=content)

    assert manifest.stringify() == content



def test_standard_get_line():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEABCDEABCDEABCDEABCDEABCDEab", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": "FU75KFU75KFU75KFU75KFU75KFU75Kfu", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": "K86TJK86TJK86TJK86TJK86TJK86TJk8", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": "12T4512T4512T4512T4512T4512T4512", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": "6H7K96H7K96H7K96H7K96H7K96H7K96h", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    assert manifest.get_line("WONDERWOMAN.EXT") == ops.manifest.ManifestEntry(attributes={"true_name": "WONDERWOMAN.EXT", "code_name": "K86TJK86TJK86TJK86TJK86TJK86TJk8", "size": 52345, "aes_key": keys[2]})


def test_missing_get_line():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEABCDEABCDEABCDEABCDEABCDEab", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": "FU75KFU75KFU75KFU75KFU75KFU75Kfu", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": "K86TJK86TJK86TJK86TJK86TJK86TJk8", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": "12T4512T4512T4512T4512T4512T4512", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": "6H7K96H7K96H7K96H7K96H7K96H7K96h", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    assert manifest.get_line("DIANA.EXT") is None


# ManifestEntry tests


def test_entry_regex_no_true():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_no_random():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "", "size": 45, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_invalid_size():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 'A', "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_no_key():
    key = ''
    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key}

    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_random_long():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJabKLMNOPQRS", "size": 45, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_random_short():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "ABC", "size": 45, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_key_long():
    key = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xd7k\xb6\xd5\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 34, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_key_short():
    key = '\xc2\x95\x1b\xbe\x80jb\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQhi", "size": 'A', "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_missing_delim():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    str_line = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,34" + key
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(str_line=str_line)


def test_parse_newline_mid():
    key = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    str_line = 'CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,10,' + key
    entry = ops.manifest.ManifestEntry(str_line=str_line)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab",
                                "size": 10, "aes_key": key}


def test_parse_newline_end():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    str_line = 'CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,10,' + key
    entry = ops.manifest.ManifestEntry(str_line=str_line)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab",
                                "size": 10, "aes_key": key}


def test_manifest_line():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab", "size": 25, "aes_key": key}
    manifest = ops.manifest.ManifestEntry(attributes=attributes)
    assert "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,25," + key == manifest.stringify()


def test_entry_from_string():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    str_entry = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,10," + key
    entry = ops.manifest.ManifestEntry(str_line=str_entry)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab",
                                "size": 10, "aes_key": key}


def test_entry_from_attributes():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    attrs = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab",
             "size": 10, "aes_key": key}
    entry = ops.manifest.ManifestEntry(attributes=attrs)
    assert entry.attributes == attrs


def test_entry_from_both():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    str_entry = "CLARK_KENT.TXT,ABCDEFGHIJABCDEFGHIJABCDEFGHIJab,10," + key
    attrs = {"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEFGHIJABCDEFGHIJABCDEFGHIJab",
             "size": 10, "aes_key": key}
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry(str_line=str_entry, attributes=attrs)


def test_entry_from_neither():
    with pytest.raises(ops.exceptions.IllegalArgumentException):
        ops.manifest.ManifestEntry()


def test_replace_manifest_update():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEABCDEABCDEABCDEABCDEABCDEab", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": "FU75KFU75KFU75KFU75KFU75KFU75Kfu", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": "K86TJK86TJK86TJK86TJK86TJK86TJk8", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": "12T4512T4512T4512T4512T4512T4512", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": "6H7K96H7K96H7K96H7K96H7K96H7K96h", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    old_code_name = manifest.update_manifest("SUPERMAN.PDF", "SNAFUSNAFUSNAFUSNAFUSNAFUSNAFUsn", 52, new_key)  # TODO: assumes we do not rotate keys
    superman = manifest.remove_line("SUPERMAN.PDF")
    old_manifest.remove_line("SUPERMAN.PDF")

    assert old_code_name == "FU75KFU75KFU75KFU75KFU75KFU75Kfu" and manifest == old_manifest and \
        superman.attributes["code_name"] == "SNAFUSNAFUSNAFUSNAFUSNAFUSNAFUsn" and superman.attributes["size"] == 52


def test_create_manifest_update():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": "ABCDEABCDEABCDEABCDEABCDEABCDEab", "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": "FU75KFU75KFU75KFU75KFU75KFU75Kfu", "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": "K86TJK86TJK86TJK86TJK86TJK86TJk8", "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": "12T4512T4512T4512T4512T4512T4512", "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": "6H7K96H7K96H7K96H7K96H7K96H7K96h", "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(ops.manifest.ManifestEntry(attributes=attr))

    manifest = ops.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    # TODO: assumes we do not rotate keys
    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    old_code_name = manifest.update_manifest("DIANA.PDF", "FUBARFUBARFUBARFUBARFUBARFUBARfu", 52, new_key)
    diana = manifest.remove_line("DIANA.PDF")

    assert old_code_name is None and old_manifest == manifest and \
        diana.attributes["code_name"] == "FUBARFUBARFUBARFUBARFUBARFUBARfu" and diana.attributes["size"] == 52
