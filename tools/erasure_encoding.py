import logging
import sys
from pyeclib.ec_iface import ECDriver
from pyeclib.ec_iface import ECInsufficientFragments
from pyeclib.ec_iface import ECInvalidFragmentMetadata
from pyeclib.ec_iface import ECDriverError
from custom_exceptions import exceptions
from tools.utils import sandbox_function

EXIT_CODE_DECODE_ERROR = 2


def _get_ecdriver(threshold, total_shares):
    return ECDriver(k=threshold, m=total_shares - threshold, ec_type='liberasurecode_rs_vand')


def _share_implementation(message, threshold, total_shares):
    ec_driver = _get_ecdriver(threshold, total_shares)
    shares = ec_driver.encode(message)
    return shares


def _reconstruct_implementation(shares, threshold, total_shares):
    try:
        ec_driver = _get_ecdriver(threshold, total_shares)
        message = ec_driver.decode(shares)
        return [message]
    except (ECInsufficientFragments, ECInvalidFragmentMetadata, ECDriverError):
        sys.exit(EXIT_CODE_DECODE_ERROR)


def share(message, threshold, total_shares):
    """
    Construct shares of the given message such that shares above the threshold recreate the message.

    Args:
        message: a binary string or other byte representation of the message to be shared.
        threshold: the number of shares required to reconstruct the message.
        total_shares: the total number of shares to return

    Returns:
        A list of values suitable to be passed to the reconstruct function.
    Raises:
        LibraryException: An exception occurred in the backing erasure encoding library.
    """
    try:
        shares = sandbox_function(_share_implementation, message, threshold, total_shares)
        return shares
    except exceptions.SandboxProcessFailure:
        logging.exception("Exception encountered during share creation")
        raise exceptions.LibraryException


def reconstruct(shares, threshold, total_shares):
    """
    Reconstruct a message if possible from the given shares.
    If the shares are corrupt, an invalid message will be returned.

    Args:
        shares: a list of equally sized binary strings.

    Returns:
        A byte representation of the reconstructed message if the reconstruction was successful.

    Raises:
        DecodeError: Decoding the erasure code was unsuccessful (e.g. the shares were of different lengths).
        LibraryException: An exception occurred in the backing erasure encoding library.
    """
    try:
        message = sandbox_function(_reconstruct_implementation, shares, threshold, total_shares)
        return message[0]
    except exceptions.SandboxProcessFailure as e:
        if e.exitcode is EXIT_CODE_DECODE_ERROR:
            raise exceptions.DecodeError
        else:
            logging.exception("Exception encountered during share reconstruction")
            raise exceptions.LibraryException
