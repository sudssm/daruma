import nacl.secret
import nacl.utils
import logging
from uuid import uuid4
from custom_exceptions import exceptions

KEY_SIZE = nacl.secret.SecretBox.KEY_SIZE
NAME_SIZE = 32


def generate_key():
    """
    Returns:
        A secret key suitable to be passed to the encrypt function.
    Raises:
        LibraryException: An exception occurred in the backing cryptographic library.
    """
    try:
        return nacl.utils.random(KEY_SIZE)

    except Exception:
        logging.exception("Exception encountered during key generation")
        raise exceptions.LibraryException


def generate_name():
    return str(uuid4()).replace('-', '').upper()
