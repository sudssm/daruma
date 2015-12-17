import algos.shamir_secret_sharing


def test_min_shares():
    # First share
    secret = "FOO BAR WOOHOO!"
    shares = algos.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = algos.shamir_secret_sharing.reconstruct(shares[0:2])
    assert recovered_secret == secret


def test_max_shares():
    # First share
    secret = "FOO BAR WOOHOO!"
    shares = algos.shamir_secret_sharing.share(secret, 2, 5)

    # Then attempt to recover
    recovered_secret = algos.shamir_secret_sharing.reconstruct(shares)
    assert recovered_secret == secret
