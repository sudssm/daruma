import logging
from custom_exceptions import exceptions
from robustsecretsharing.schemes import sss


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
        LibraryException: an exception was thrown by the supporting sharing library
    """
    try:
        return sss.share_secret(total_shares, threshold, len(secret), secret)
    except Exception:
        logging.exception("Exception encountered during secret share creation")
        raise exceptions.LibraryException


def reconstruct(shares, secret_length, total_shares):
    """
    Reconstruct a secret if possible from the given shares.
    If the shares are corrupt or the given number of shares is less than the
    recreation threshold, invalid data will be returned.

    Args:
        shares: a list of properly formatted binary strings.
        total_shares: the maximum number of shares, so total_shares >= len(shares)
        secret_length: the value that would be returned by len(secret)
    Returns:
        A byte representation of the reconstructed secret.
    Raises:
        LibraryException: an exception was thrown by the supporting sharing library
    """
    try:
        return sss.reconstruct_secret(total_shares, secret_length, shares)
    except Exception:
        logging.exception("Exception encountered during secret share reconstruction")
        raise exceptions.LibraryException
