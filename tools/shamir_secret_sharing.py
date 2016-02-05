import binascii
import logging
from secretsharing import SecretSharer
from custom_exceptions import exceptions


def share(secret, threshold, total_shares):
    """
    Construct shares of the given secret such that shares below the threshold
    yield no information, but shares above the threshold recreate the secret.

    Args:
        secret: a binary string or other byte representation of the secret to be shared.
        threshold: the number of shares required to reconstruct the secret.
        total_shares: the total number of shares to return

    Returns:
        A list of values suitable to be passed to the reconstruct function.

    Raises:
        LibraryException: An exception occurred in the backing secret sharing library.
    """
    try:
        return SecretSharer.split_secret(binascii.hexlify(secret), threshold, total_shares)
    except Exception:
        logging.exception("Exception encountered during secret share creation")
        raise exceptions.LibraryException


def reconstruct(shares):
    """
    Reconstruct a secret if possible from the given shares.
    If the shares are corrupt or the given number of shares is less than the
    recreation threshold, invalid data will be returned.

    Args:
        shares: a list of properly formatted binary strings.

    Returns:
        A byte representation of the reconstructed secret.

    Raises:
        DecodeError: Decoding the secret was unsuccessful (e.g. the shares were improperly formatted).

    Raises:
        LibraryException: An exception occurred in the backing secret sharing library.
    """
    try:
        secret = SecretSharer.recover_secret(shares)
    except ValueError:
        raise exceptions.DecodeError
    except Exception:
        logging.exception("Exception encountered during secret share reconstruction")
        raise exceptions.LibraryException

    return binascii.unhexlify(secret)
