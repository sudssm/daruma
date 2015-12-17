import algos.encryption
import pytest


def test_standard_usage():
    # First encrypt
    plaintext = "FOO BAR WOOHOO!"
    ciphertext, key = algos.encryption.encrypt(plaintext)

    # Then attempt to decrypt
    recovered_plaintext = algos.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_empty_plaintext():
    # First encrypt
    plaintext = ""
    ciphertext, key = algos.encryption.encrypt(plaintext)

    # Then attempt to decrypt
    recovered_plaintext = algos.encryption.decrypt(ciphertext, key)
    assert recovered_plaintext == plaintext


def test_malicious_ciphertext():
    # First encrypt
    plaintext = "FOO BAR woohoo!"
    ciphertext, key = algos.encryption.encrypt(plaintext)

    # Then attempt to decrypt
    malicious_ciphertext = ciphertext[0:5] + 'C' + ciphertext[6:]
    with pytest.raises(algos.encryption.DecryptError):
        algos.encryption.decrypt(malicious_ciphertext, key)
