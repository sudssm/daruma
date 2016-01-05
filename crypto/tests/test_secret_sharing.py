import crypto.shamir_secret_sharing
from custom_exceptions import exceptions
from crypto.encryption import generate_key
import pytest

secret = generate_key()
def test_min_shares():
    # First share
    shares = crypto.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = crypto.shamir_secret_sharing.reconstruct(shares[0:2])
    assert recovered_secret == secret


def test_max_shares():
    # First share
    shares = crypto.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = crypto.shamir_secret_sharing.reconstruct(shares)
    assert recovered_secret == secret


def test_invalid_share_formatting():
    # First share
    shares = crypto.shamir_secret_sharing.share(secret, 2, 5)

    # Then corrupt shares
    new_shares = [shares[0], "woohoo!"]

    # Then attempt to recover
    with pytest.raises(exceptions.SecretReconstructionError):
        crypto.shamir_secret_sharing.reconstruct(new_shares)
