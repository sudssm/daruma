import managers.manifest
from custom_exceptions import exceptions
from tools.encryption import generate_key
import copy
import pytest

# Manifest tests
codename1 = "ABCDEABCDEABCDEABCDEABCDEABCDEAB"
codename2 = "HIJKLMNOPQHIJKLMNOPQHIJKLMNOPQHI"
codename3 = "K86TJK86TJK86TJK86TJK86TJK86TJK8"
codename4 = "12T4512T4512T4512T4512T4512T4512"
codename5 = "6H7K96H7K96H7K96H7K96H7K96H7K96H"
codename6 = "SNAFUSNAFUSNAFUSNAFUSNAFUSNAFUSN"


def test_regex_standard():
    key1 = generate_key()
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_start():
    key1 = '\n\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_mid():
    key1 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_newline_end():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_start():
    key1 = ',\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_mid():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>,\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_comma_end():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.lines) == sorted(entries)


def test_regex_no_true():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()

    content = "," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_no_random():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF,,45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_no_size():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_no_key():
    key1 = ''
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_random_long():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + "," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename1 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_random_short():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF,ABC,45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_key_long():
    key1 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xd7k\xb6\xd5\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_key_short():
    key1 = '\xc2\x95\x1b\xbe\x80jb\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34," + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_regex_missing_delim():
    key1 = generate_key()
    key2 = generate_key()

    content = "CLARK_KENT.TXT," + codename1 + ",34" + key1 + "\n" + \
              "SUPERMAN.PDF," + codename2 + ",45," + key2 + "\n"

    with pytest.raises(exceptions.ParseException):
        managers.manifest.Manifest(content=content)


def test_empty_ls():
    empty = managers.manifest.Manifest(content="")
    assert empty.ls() == []


def test_standard_ls_lines():
    key1 = generate_key()
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    manifest = managers.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_standard_ls_content():
    key1 = generate_key()
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_mid_ls_lines():
    key1 = generate_key()
    key2 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    manifest = managers.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_end_ls_lines():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    manifest = managers.manifest.Manifest(lines=entries)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_mid_ls_content():
    key1 = generate_key()
    key2 = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_newline_end_ls_content():
    key1 = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    key2 = generate_key()
    entries = []

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key1}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key2}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)

    assert sorted(manifest.ls()) == ["CLARK_KENT.TXT", "SUPERMAN.PDF"]


def test_manifest_from_list():
    entries = []
    key = generate_key()

    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 45, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    manifest = managers.manifest.Manifest(lines=entries)
    assert str(manifest) == "CLARK_KENT.TXT," + codename1 + ",34," + key + "\n" + \
                            "SUPERMAN.PDF," + codename2 + ",45," + key + "\n"


def test_manifest_from_content():
    entries = []
    key = generate_key()

    attributes = {"true_name": "FIREFLY.TXT", "code_name": codename1, "size": 34, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SERENITY.PDF", "code_name": codename2, "size": 45, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    manifest = managers.manifest.Manifest(content=content)
    assert str(manifest) == "FIREFLY.TXT," + codename1 + ",34," + key + "\n" + \
                            "SERENITY.PDF," + codename2 + ",45," + key + "\n"


def test_manifest_from_both():
    entries = []
    key = generate_key()

    attributes = {"true_name": "FIREFLY.TXT", "code_name": codename1, "size": 34, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))
    attributes = {"true_name": "SERENITY.PDF", "code_name": codename2, "size": 45, "aes_key": key}
    entries.append(managers.manifest.ManifestEntry(attributes=attributes))

    content = ""
    for entry in entries:
        content += str(entry) + "\n"

    with pytest.raises(exceptions.IllegalArgumentException):
        managers.manifest.Manifest(lines=entries, content=content)


def test_manifest_from_neither():
    manifest = managers.manifest.Manifest()
    assert manifest.lines == []


def test_manifest_from_list_empty():
    entries = []
    manifest = managers.manifest.Manifest(lines=entries)
    assert manifest.lines == []


def test_manifest_from_content_empty():
    content = ""
    manifest = managers.manifest.Manifest(content=content)
    assert manifest.lines == []


def test_roundtrip_empty():
    content = ""
    manifest = managers.manifest.Manifest(content=content)

    assert str(manifest) == content


def test_standard_get_line():
    keys = []
    for i in range(5):
        keys.append(generate_key())
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": codename3, "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": codename4, "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": codename5, "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(managers.manifest.ManifestEntry(attributes=attr))

    manifest = managers.manifest.Manifest(lines=entries)
    assert manifest.get_line("WONDERWOMAN.EXT") == {"true_name": "WONDERWOMAN.EXT", "code_name": codename3, "size": 52345, "aes_key": keys[2]}


def test_missing_get_line():
    keys = []
    for i in range(5):
        keys.append(generate_key())
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": codename3, "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": codename4, "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": codename5, "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(managers.manifest.ManifestEntry(attributes=attr))

    manifest = managers.manifest.Manifest(lines=entries)
    with pytest.raises(exceptions.FileNotFound):
        manifest.get_line("DIANA.EXT")


# ManifestEntry tests


def test_entry_regex_no_true():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "", "code_name": codename1, "size": 34, "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_no_random():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "", "size": 45, "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_invalid_size():
    key = generate_key()

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 'A', "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_no_key():
    key = ''
    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key}

    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_random_long():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb,'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename1 + "a", "size": 45, "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_random_short():
    key = generate_key()

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": "ABC", "size": 45, "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_key_long():
    key = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xd7k\xb6\xd5\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 34, "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_key_short():
    key = '\xc2\x95\x1b\xbe\x80jb\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'

    attributes = {"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 'A', "aes_key": key}
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(attributes=attributes)


def test_entry_regex_missing_delim():
    key = generate_key()

    str_line = "CLARK_KENT.TXT," + codename1 + ",34" + key
    with pytest.raises(exceptions.ParseException):
        managers.manifest.ManifestEntry(str_line=str_line)


def test_parse_newline_mid():
    key = '\xc2\x95\x1b\xbe\xd3Z\xcaR\x80jb\xd7k\xb6\xd5\x8ezxw\xb3\x11;\x1b\xba\n\xdf\xe6.=\xb4\x96&'
    str_line = 'CLARK_KENT.TXT,' + codename1 + ',10,' + key
    entry = managers.manifest.ManifestEntry(str_line=str_line)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": codename1,
                                "size": 10, "aes_key": key}


def test_parse_newline_end():
    key = '\x9d\xee9I\x99\xef\x18U\x94\x15\x13V\xe6\xd5D~\x8d\xd2>\x07d\x11\x86\xb6\xf2x!\x91/\xd0\xbb\n'
    str_line = 'CLARK_KENT.TXT,' + codename1 + ',10,' + key
    entry = managers.manifest.ManifestEntry(str_line=str_line)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": codename1,
                                "size": 10, "aes_key": key}


def test_manifest_line():
    key = generate_key()
    attributes = {"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 25, "aes_key": key}
    manifest = managers.manifest.ManifestEntry(attributes=attributes)
    assert "CLARK_KENT.TXT," + codename1 + ",25," + key == str(manifest)


def test_entry_from_string():
    key = generate_key()
    str_entry = "CLARK_KENT.TXT," + codename1 + ",10," + key
    entry = managers.manifest.ManifestEntry(str_line=str_entry)
    assert entry.attributes == {"true_name": "CLARK_KENT.TXT", "code_name": codename1,
                                "size": 10, "aes_key": key}


def test_entry_from_attributes():
    key = generate_key()
    attrs = {"true_name": "CLARK_KENT.TXT", "code_name": codename1,
             "size": 10, "aes_key": key}
    entry = managers.manifest.ManifestEntry(attributes=attrs)
    assert entry.attributes == attrs


def test_entry_from_both():
    key = generate_key()
    str_entry = "CLARK_KENT.TXT" + codename1 + "," + key
    attrs = {"true_name": "CLARK_KENT.TXT", "code_name": codename1,
             "size": 10, "aes_key": key}
    with pytest.raises(exceptions.IllegalArgumentException):
        managers.manifest.ManifestEntry(str_line=str_entry, attributes=attrs)


def test_entry_from_neither():
    with pytest.raises(exceptions.IllegalArgumentException):
        managers.manifest.ManifestEntry()


def test_replace_manifest_update():
    keys = []
    for i in range(5):
        keys.append(generate_key())
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": codename3, "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": codename4, "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": codename5, "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(managers.manifest.ManifestEntry(attributes=attr))

    manifest = managers.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    new_key = generate_key()
    old_code_name = manifest.update_manifest("SUPERMAN.PDF", codename6, 52, new_key)  # TODO: assumes we do not rotate keys
    superman = manifest.remove_line("SUPERMAN.PDF")
    old_manifest.remove_line("SUPERMAN.PDF")

    assert old_code_name == codename2 and manifest == old_manifest and \
        superman["code_name"] == codename6 and superman["size"] == 52


def test_create_manifest_update():
    keys = []
    for i in range(5):
        keys.append(generate_key())
    attributes = []
    entries = []

    attributes.append({"true_name": "CLARK_KENT.TXT", "code_name": codename1, "size": 9345, "aes_key": keys[0]})
    attributes.append({"true_name": "SUPERMAN.PDF", "code_name": codename2, "size": 345, "aes_key": keys[1]})
    attributes.append({"true_name": "WONDERWOMAN.EXT", "code_name": codename3, "size": 52345, "aes_key": keys[2]})
    attributes.append({"true_name": "BATMAN.DOC", "code_name": codename4, "size": 586, "aes_key": keys[3]})
    attributes.append({"true_name": "IF3685.TIOY4ET", "code_name": codename5, "size": 90, "aes_key": keys[4]})

    for attr in attributes:
        entries.append(managers.manifest.ManifestEntry(attributes=attr))

    manifest = managers.manifest.Manifest(lines=entries)
    old_manifest = copy.deepcopy(manifest)

    new_key = generate_key()
    old_code_name = manifest.update_manifest("DIANA.PDF", codename6, 52, new_key)
    diana = manifest.remove_line("DIANA.PDF")

    assert old_code_name is None and old_manifest == manifest and \
        diana["code_name"] == codename6 and diana["size"] == 52
