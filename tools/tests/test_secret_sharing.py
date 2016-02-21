from custom_exceptions import exceptions
import tools.shamir_secret_sharing
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key


def test_min_shares():
    total_shares = 5
    threshold = 2
    # First share
    shares = tools.shamir_secret_sharing.share(secret, threshold, total_shares)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares[0:threshold], len(secret), total_shares)
    assert recovered_secret == secret


def test_max_shares():
    total_shares = 5
    threshold = 2
    # First share
    shares = tools.shamir_secret_sharing.share(secret, threshold, total_shares)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares, len(secret), total_shares)
    assert recovered_secret == secret


def test_invalid_share_formatting():
    total_shares = 5
    threshold = 2
    # First share
    shares = tools.shamir_secret_sharing.share(secret, threshold, total_shares)

    # Then corrupt shares
    new_shares = [shares[0], "woohoo!"]

    # Then attempt to recover
    with pytest.raises(exceptions.LibraryException):
        tools.shamir_secret_sharing.reconstruct(new_shares, len(secret), total_shares)


def test_secret_with_leading_zeroes():
    total_shares = 5
    threshold = 2

    # Create secret
    my_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key

    # Then share
    shares = tools.shamir_secret_sharing.share(my_secret, threshold, total_shares)

    # Then attempt to recover
    recovered_secret = tools.shamir_secret_sharing.reconstruct(shares[0:2], len(secret), total_shares)
    assert recovered_secret == my_secret


def test_bad_configuration():
    total_shares = 2
    threshold = 5

    with pytest.raises(exceptions.LibraryException):
        tools.shamir_secret_sharing.share(secret, threshold, total_shares)
