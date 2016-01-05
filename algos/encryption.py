import nacl.secret
import nacl.utils
import nacl.exceptions


class DecryptError(Exception):
    """
    Exception for errors in decryption and/or authentication
    """


def encrypt(plaintext, key = None):
    """
    Encrypt the given plaintext with an automatically generated key using an authenticated encryption scheme.

    Args:
        plaintext: a string or other byte representation of the plaintext to be encrypted.
        key: an optional key; one will be generated if not provided
    Returns:
        A tuple (ciphertext, key) containing values suitable to be passed to the decrypt function.
    """
    if key is None:
      key = generate_key()
    box = nacl.secret.SecretBox(key)

    # A new random nonce is selected for each encryption - this may not be
    # necessary, since we also generate new random keys for each encryption.
    nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

    ciphertext = box.encrypt(plaintext, nonce)

    return ciphertext, key

def generate_key():
  return nacl.utils.random(nacl.secret.SecretBox.KEY_SIZE)

def decrypt(ciphertext, key):
    """
    Decrypt the given ciphertext with the given key and verify the authentication.

    Args:
        cipher: a string or other byte representation of the ciphertext to be decrypted.
        key: a byte representation of the key used to decrypt the ciphertext

    Returns:
        A byte representation of the decrypted plaintext if the decryption was successful.

    Raises:
        CryptoError: Decryption or authentication was unsuccessful.
    """
    box = nacl.secret.SecretBox(key)

    # Note that the nonce is automatically bundled with the ciphertext
    try:
        plaintext = box.decrypt(ciphertext)
    except nacl.exceptions.CryptoError:
        raise DecryptError

    return plaintext
