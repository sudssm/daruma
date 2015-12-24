import ops.operations


def standard_ls():
    manifest = "clark_kent.txt\tabcde\t1234567\nsuperman.pdf\tfghijklmnopqrs\t89101112131415\n"
    assert ops.operations.ls(manifest) == ["clark_kent.txt", "superman.pdf"]


def empty_ls():
    manifest = ""
    assert ops.operations.ls(manifest) == []


def standard_get():
    pass


def missing_get():
    pass


def multislice_get():
    pass


def create_put():
    pass


def replace_put():
    pass


def multislice_create_put():
    pass


def multislice_replace_put():
    pass


def standard_delete():
    pass


def missing_delete():
    pass
