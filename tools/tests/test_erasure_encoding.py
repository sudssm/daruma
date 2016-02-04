import tools.erasure_encoding
from custom_exceptions import exceptions
import pytest


def test_min_shares():
    # First share
    message = "FOO BAR WOOHOO!"
    shares = tools.erasure_encoding.share(message, 2, 5)

    # Then attempt to recover
    recovered_message = tools.erasure_encoding.reconstruct(shares[0:2], 2, 5)
    assert recovered_message == message


def test_max_shares():
    # First share
    message = "FOO BAR WOOHOO!"
    shares = tools.erasure_encoding.share(message, 2, 5)

    # Then attempt to recover
    recovered_message = tools.erasure_encoding.reconstruct(shares, 2, 5)
    assert recovered_message == message


def test_insufficient_shares():
    # First share
    message = "FOO BAR WOOHOO!"
    shares = tools.erasure_encoding.share(message, 2, 5)

    # Then attempt to recover
    with pytest.raises(exceptions.DecodeError):
        tools.erasure_encoding.reconstruct(shares[0:1], 2, 5)


def test_corrupt_shares_wrong_sizes():
    # First share
    message1 = "FOO BAR woohoo!"
    shares1 = tools.erasure_encoding.share(message1, 3, 5)

    message2 = "Definitely the wrongs size"
    shares2 = tools.erasure_encoding.share(message2, 3, 5)

    # Then partially corrupt shares
    new_shares = [shares1[0], shares2[0], shares1[1], shares1[2]]

    # Then attempt to decode
    with pytest.raises(exceptions.DecodeError):
        tools.erasure_encoding.reconstruct(new_shares, 2, 5)


def test_bad_configuration():
    message1 = "FOO BAR woohoo!"
    with pytest.raises(exceptions.LibraryException):
        tools.erasure_encoding.share(message1, 5, 3)
