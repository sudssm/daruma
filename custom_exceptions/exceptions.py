# Exceptions used in SecretBox


# general exceptions
class LibraryException(Exception):
    """
    Indicates a non-recoverable error generated in a call to an external library
    """


# Should we get rid of this?
class IllegalArgumentException(Exception):
    """
    Passed invalid arguments to a constructor or method
    """


class NetworkException(Exception):
    """
    Not connected to the internet
    """


# provider exceptions
class ConnectionFailure(Exception):
    """
    Provider is considered off-line
    """


class AuthFailure(Exception):
    """
    Failed to authenticate the API token with the provider
    """


class OperationFailure(Exception):
    """
    The provider rejected the desired operation (reason unknown)
    """


# crypto exceptions
class DecryptError(Exception):
    """
    Exception for errors in decryption and/or authentication
    """


class DecodeError(Exception):
    """
    Exception for errors in decoding an erasure code
    """


# manifest exceptions
class ParseException(Exception):
    """
    Argument provided could not be parsed by the relevant regex
    """


class FileNotFound(Exception):
    """
    User requests a file by name that cannot be located in the manifest
    """


# manager exceptions
class ManifestGetError(Exception):
    """
    Thrown when there was an error recovering the manifest
    """


class KeyReconstructionError(Exception):
    """
    Exception for errors in decoding a secret
    """


class FileReconstructionError(Exception):
    """
    Exception for errors in decoding a file
    """
