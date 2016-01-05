import crypto.encryption
from custom_exceptions import exceptions
import pytest


def test_standard_usage():
    # First encrypt
    plaintext = "FOO BAR WOOHOO!"
    ciphertext, key = crypto.encryption.encrypt(plaintext)

    # Then attempt to decrypt
    recovered_plaintext = crypto.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_empty_plaintext():
    # First encrypt
    plaintext = ""
    ciphertext, key = crypto.encryption.encrypt(plaintext)

    # Then attempt to decrypt
    recovered_plaintext = crypto.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_malicious_ciphertext():
    # First encrypt
    plaintext = "FOO BAR woohoo!"
    ciphertext, key = crypto.encryption.encrypt(plaintext)

    # Then corrupt ciphertext
    malicious_ciphertext = ciphertext[0:5] + 'C' + ciphertext[6:]

    # Then attempt to decrypt
    with pytest.raises(exceptions.DecryptError):
        crypto.encryption.decrypt(malicious_ciphertext, key)
