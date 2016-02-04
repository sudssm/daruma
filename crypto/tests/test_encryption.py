import crypto.encryption
from custom_exceptions import exceptions
import pytest


def test_standard_usage():
    # First encrypt
    plaintext = "FOO BAR WOOHOO!"
    key = crypto.encryption.generate_key()
    ciphertext = crypto.encryption.encrypt(plaintext, key)

    # Then attempt to decrypt
    recovered_plaintext = crypto.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_empty_plaintext():
    # First encrypt
    plaintext = ""
    key = crypto.encryption.generate_key()
    ciphertext = crypto.encryption.encrypt(plaintext, key)

    # Then attempt to decrypt
    recovered_plaintext = crypto.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_malicious_ciphertext():
    # First encrypt
    plaintext = "FOO BAR woohoo!"
    key = crypto.encryption.generate_key()
    ciphertext = crypto.encryption.encrypt(plaintext, key)

    # Then corrupt ciphertext
    malicious_ciphertext = ciphertext[0:5] + 'C' + ciphertext[6:]

    # Then attempt to decrypt
    with pytest.raises(exceptions.DecryptError):
        crypto.encryption.decrypt(malicious_ciphertext, key)


def test_short_encryption_key():
    # Set up a normal encryption
    plaintext = "FOO BAR woohoo!"
    key = crypto.encryption.generate_key()

    # Drop a few bytes from the key
    short_key = key[:-3]

    with pytest.raises(exceptions.LibraryException):
        crypto.encryption.encrypt(plaintext, short_key)
