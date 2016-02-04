import tools.shamir_secret_sharing
from custom_exceptions import exceptions
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key


def test_min_shares():
    # First share
    shares = tools.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares[0:2])
    assert recovered_secret == secret


def test_max_shares():
    # First share
    shares = tools.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares)
    assert recovered_secret == secret


def test_invalid_share_formatting():
    # First share
    shares = tools.shamir_secret_sharing.share(secret, 2, 5)

    # Then corrupt shares
    new_shares = [shares[0], "woohoo!"]

    # Then attempt to recover
    with pytest.raises(exceptions.DecodeError):
        tools.shamir_secret_sharing.reconstruct(new_shares)


def test_secret_with_leading_zeroes():
    # Create secret
    my_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key

    # Then share
    shares = tools.shamir_secret_sharing.share(my_secret, 2, 5)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares[0:2])
    assert recovered_secret == my_secret


def test_bad_configuration():
    with pytest.raises(exceptions.LibraryException):
        tools.shamir_secret_sharing.share(secret, 5, 2)
