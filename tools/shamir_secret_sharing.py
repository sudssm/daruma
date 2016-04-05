import logging
from custom_exceptions import exceptions
from robustsecretsharing import rss


def share(secret, player_ids, threshold):
    """
    Construct shares of the given secret such that shares below the threshold
    yield no information, but shares above the threshold recreate the secret.

    Args:
        secret: a binary string or other byte representation of the secret to be shared.
        player_ids: a list of unique strings, one for each resulting share
        threshold: the number of shares required to reconstruct the secret.
    Returns:
        A map from player_id to a share to give to that player, suitable to be passed into reconstruct
    Raises:
        LibraryException: an exception was thrown by the supporting sharing library
    """
    try:
        return rss.share_authenticated_secret(player_ids, threshold, len(secret), secret)
    except ValueError:
        logging.exception("Exception encountered during secret share creation")
        raise exceptions.LibraryException


def reconstruct(shares_map, secret_length, total_shares, threshold):
    """
    Reconstruct a secret if possible from the given shares.
    If the shares are corrupt or the given number of shares is less than the
    recreation threshold, invalid data will be returned.

    Args:
        shares_map: a map of player_id to the share assigned to that player in call to share
        secret_length: the length of the secret that was shared
        total_shares: the original number of shares created
        threshold: the number of shares required to reconstruct the secret.
    Returns:
        If successful
        (secret, honest_players, dishonest_players)
        secret: the original bytestring that was shared by share_authenticated_secret
        honest_players: a non-exhaustive list of players whose shares could be used for reconstruction of that secret
        dishonest_players: a non-exhaustive list of dishonest players (specifically those whose shares caused structural errors)
    Raises:
        ReconstructionError: the underlying library could not reconstruct
        LibraryException: an exception was thrown by the supporting sharing library
    """
    try:
        return rss.reconstruct_authenticated_secret(total_shares, threshold, secret_length, shares_map)
    except rss.FatalReconstructionFailure:
        logging.exception("Exception encountered during secret share reconstruction")
        raise exceptions.ReconstructionError


def verify(shares_map, test_secret, total_shares):
    """
    Check to see if the unauthenticated Shamir recovery of shares_map results in test_secret
    Args:
        shares_map: a map of player_id to the share assigned to that player in call to share
        test_secret: a potential secret to check of the same size as the originally shared secret
        total_shares: the original number of shares created
    Returns True if the shares_map successfully recovers test_secret
    """
    try:
        return test_secret == rss.reconstruct_unauthenticated_secret(total_shares, len(test_secret), shares_map)
    except:
        return False
