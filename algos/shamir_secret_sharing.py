import binascii
from secretsharing import SecretSharer


def share(secret, threshold, total_shares):
    """
    Construct shares of the given secret such that shares below the threshold yield no information, but shares above the threshold recreate the secret.

    Args:
        secret: a binary string or other byte representation of the secret to be shared.
        threshold: the number of shares required to reconstruct the secret.
        total_shares: the total number of shares to return

    Returns:
        A list of values suitable to be passed to the reconstruct function.
    """
    return SecretSharer.split_secret(binascii.hexlify(secret), threshold, total_shares)


def reconstruct(shares):
    """
    Reconstruct a secret if possible from the given shares.  If the given number of shares is less than the recreation threshold, garbage data will still be returned.

    Args:
        shares: a list of binary strings.

    Returns:
        A byte representation of the reconstructed secret.
    """
    secret = SecretSharer.recover_secret(shares)
    return binascii.unhexlify(secret)
