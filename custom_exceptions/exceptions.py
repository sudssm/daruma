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
    def __init__(self, provider):
        self.provider = provider


class AuthFailure(Exception):
    """
    Failed to authenticate the API token with the provider
    """
    def __init__(self, provider):
        self.provider = provider


class ProviderOperationFailure(Exception):
    """
    The provider rejected the desired operation (reason unknown)
    """
    def __init__(self, provider):
        self.provider = provider


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
class OperationFailure(Exception):
    """
    A multi-provider operation had some failure, but was not fatal
    Must contain the result of the operation, and the list of failures
    Raised only by read operations - any failure in a write operation will be fatal
    result should only be None if the original operation wasn't supposed to return anything
    failures - a list of Exceptions, thrown by some provider
    """
    def __init__(self, failures, result):
        self.failures = failures
        self.result = result


class FatalOperationFailure(Exception):
    """
    A multi-provider operation had some failure that was fatal
    failures - a list of Exceptions, thrown by some provider
    """
    def __init__(self, failures):
        self.failures = failures
