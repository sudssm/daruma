import ops.operations
import nacl.utils
import nacl.secret


def test_manifest_line():
    key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    assert "clark_kent.txt\tabcde\t" + key + "\n" == ops.operations.manifest_line("clark_kent.txt", "abcde", key)


def test_standard_ls():
    key1 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    key2 = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

    manifest = ""
    manifest += ops.operations.manifest_line("clark_kent.txt", "abcdefg", key1)
    manifest += ops.operations.manifest_line("superman.pdf", "hijklmn", key2)

    assert ops.operations.get_file_list(manifest) == ["clark_kent.txt", "superman.pdf"]


def test_empty_ls():
    manifest = ""
    assert ops.operations.get_file_list(manifest) == []


def test_standard_get():
    pass


def test_missing_get():
    pass


def test_multislice_get():
    pass


def test_create_manifest_update():
    rand_length = 5

    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    manifest = ""
    manifest += ops.operations.manifest_line("clark_kent.txt", "abcde", keys[0])
    manifest += ops.operations.manifest_line("superman.pdf", "fu75k", keys[1])
    manifest += ops.operations.manifest_line("wonderwoman.ext", "k86tj", keys[2])
    manifest += ops.operations.manifest_line("batman.doc", "12t45", keys[3])
    manifest += ops.operations.manifest_line("if3685.tioy4et", "6h7k9", keys[4])

    # TODO: assumes we do not rotate keys
    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    tup = ops.operations.update_manifest(manifest, "superman.pdf", "snafu", new_key)
    old_rand_name = tup[0]
    new_manifest = tup[1]

    index = manifest.index("superman.pdf\t") + len("superman.pdf\t")
    assert old_rand_name == "fu75k" and manifest[:index] == new_manifest[:index] and \
        new_manifest[index: index + rand_length] == "snafu" and \
        manifest[index + rand_length:] == new_manifest[index + rand_length:]


def test_replace_manifest_update():
    keys = []
    for i in range(5):
        keys.append(nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE))
    manifest = ""
    manifest += ops.operations.manifest_line("clark_kent.txt", "abcde", keys[0])
    manifest += ops.operations.manifest_line("superman.pdf", "fu75k", keys[1])
    manifest += ops.operations.manifest_line("wonderwoman.ext", "k86tj", keys[2])
    manifest += ops.operations.manifest_line("batman.doc", "12t45", keys[3])
    manifest += ops.operations.manifest_line("if3685.tioy4et", "6h7k9", keys[4])

    # TODO: assumes we do not rotate keys
    new_key = nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)
    tup = ops.operations.update_manifest(manifest, "diana.pdf", "fubar", new_key)
    old_rand_name = tup[0]
    new_manifest = tup[1]

    assert old_rand_name is None and manifest == new_manifest[:len(manifest)] and \
        new_manifest[len(manifest):] == ops.operations.manifest_line("diana.pdf", "fubar", new_key)


def test_multislice_create_put():
    pass


def test_multislice_replace_put():
    pass


def test_standard_delete():
    pass


def test_missing_delete():
    pass
