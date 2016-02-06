from uuid import uuid4

NAME_SIZE = 32


def generate_name():
    return str(uuid4()).replace('-', '').upper()
