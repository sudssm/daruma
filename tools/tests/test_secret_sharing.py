from custom_exceptions import exceptions
import tools.shamir_secret_sharing
import pytest

secret = 'x\x02e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key


def test_min_shares():
    total_shares = 5
    threshold = 2
    # First share
    shares_map = tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)

    # Then attempt to recover
    small_shares_map = {player: share for (player, share) in shares_map.items()[0:threshold]}
    recovered_secret, _, _ = tools.shamir_secret_sharing.reconstruct(small_shares_map, len(secret), total_shares, threshold)
    assert recovered_secret == secret


def test_max_shares():
    total_shares = 5
    threshold = 2
    # First share
    shares_map = tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)

    # Then attempt to recover
    recovered_secret, _, _ = tools.shamir_secret_sharing.reconstruct(shares_map, len(secret), total_shares, threshold)
    assert recovered_secret == secret


def test_invalid_share_formatting():
    total_shares = 5
    threshold = 2
    # First share
    shares_map = tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)

    # Then corrupt shares
    corrupt_key = shares_map.keys()[0]
    shares_map[corrupt_key] = "woohoo!"

    recovered_secret, _, errors = tools.shamir_secret_sharing.reconstruct(shares_map, len(secret), total_shares, threshold)
    assert recovered_secret == secret
    assert errors == [corrupt_key]


def test_secret_with_leading_zeroes():
    total_shares = 5
    threshold = 2

    # Create secret
    my_secret = '\x00\x00e\x9c\x9e\x16\xe9\xea\x15+\xbf]\xebx;o\xef\xc9X1c\xaepj\xebj\x12\xe3r\xcd\xeaM'  # An example key

    # Then share
    shares_map = tools.shamir_secret_sharing.share(my_secret, map(str, range(total_shares)), threshold)

    small_shares_map = {player: share for (player, share) in shares_map.items()[0:threshold]}
    # Then attempt to recover
    recovered_secret, _, _ = tools.shamir_secret_sharing.reconstruct(small_shares_map, len(secret), total_shares, threshold)
    assert recovered_secret == my_secret


def test_corrupt_id():
    total_shares = 5
    threshold = 2
    # First share
    shares_map = tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)

    # Then corrupt shares
    tmp = shares_map["2"]
    shares_map["2"] = shares_map["4"]
    shares_map["4"] = tmp

    # Then attempt to recover
    recovered_secret, good, _ = tools.shamir_secret_sharing.reconstruct(shares_map, len(secret), total_shares, threshold)
    assert recovered_secret == secret
    assert "2" not in good
    assert "4" not in good


def test_bad_configuration():
    total_shares = 2
    threshold = 5

    with pytest.raises(exceptions.LibraryException):
        tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)


def test_verify():
    total_shares = 5
    threshold = 2
    # First share
    shares_map = tools.shamir_secret_sharing.share(secret, map(str, range(total_shares)), threshold)

    assert tools.shamir_secret_sharing.verify(shares_map, secret, total_shares)

    # Then corrupt shares

    shares_map = {"0": shares_map["0"], "1": "foo"}

    assert not tools.shamir_secret_sharing.verify(shares_map, secret, total_shares)
