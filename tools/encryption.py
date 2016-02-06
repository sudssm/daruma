import logging
import nacl.secret
import nacl.utils
import nacl.exceptions
from custom_exceptions import exceptions

KEY_SIZE = nacl.secret.SecretBox.KEY_SIZE


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


def encrypt(plaintext, key):
    """
    Encrypt the given plaintext with key generated with generate_key

    Args:
        plaintext: a string or other byte representation of the plaintext to be encrypted.
        key: a key returned by the generate_key function
    Returns:
        The ciphertext, suitable to be passed to the decrypt function.
    Raises:
        LibraryException: An exception occurred in the backing cryptographic library.
    """
    try:
        box = nacl.secret.SecretBox(key)

        # A new random nonce is selected for each encryption - this may not be
        # necessary, since we also generate new random keys for each encryption.
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        ciphertext = box.encrypt(plaintext, nonce)

        return ciphertext

    except Exception:
        logging.exception("Exception encountered during encryption")
        raise exceptions.LibraryException


def decrypt(ciphertext, key):
    """
    Decrypt the given ciphertext with the given key and verify the authentication.

    Args:
        cipher: a string or other byte representation of the ciphertext to be decrypted.
        key: a byte representation of the key used to decrypt the ciphertext

    Returns:
        A byte representation of the decrypted plaintext if the decryption was successful.

    Raises:
        DecryptError: Decryption or authentication was unsuccessful.
    Raises:
        LibraryException: An exception occurred in the backing cryptographic library.
    """
    try:
        box = nacl.secret.SecretBox(key)

        # Note that the nonce is automatically bundled with the ciphertext
        plaintext = box.decrypt(ciphertext)

        return plaintext

    except nacl.exceptions.CryptoError:
        raise exceptions.DecryptError
    except Exception:
        logging.exception("Exception encountered during decryption")
        raise exceptions.LibraryException
