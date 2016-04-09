# Exceptions used in SecretBox


# general exceptions
class LibraryException(Exception):
    """
    Indicates a non-recoverable error generated in a call to an external library
    """


class IllegalArgumentException(Exception):
    """
    Passed invalid arguments to a constructor or method
    """


class NetworkException(Exception):
    """
    Not connected to the internet
    """


# tools exceptions
class SandboxProcessFailure(Exception):
    """
    A function run in the process sandbox exited with an unsuccessful exit code.
    The exit code is stored in the exitcode field.
    """
    def __init__(self, exitcode):
        self.exitcode = exitcode


# provider exceptions
class ProviderFailure(Exception):
    """
    Class of exceptions that capture an individual provider failing
    """
    def __init__(self, provider):
        self.provider = provider
        provider.log_error(self)

    def __str__(self):
        return "<" + self.__class__.__name__ + " in " + str(self.provider) + ">"


class ConnectionFailure(ProviderFailure):
    """
    Provider is considered off-line
    """


class AuthFailure(ProviderFailure):
    """
    Failed to authenticate the API token with the provider
    """


class ProviderOperationFailure(ProviderFailure):
    """
    The provider rejected the desired operation (reason unknown)
    """


class InvalidShareFailure(ProviderFailure):
    """
    The provider returned the wrong value for a file
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


class ReconstructionError(Exception):
    """
    Exception for errors in reconstructing Shamir-Shared secrets
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


class InvalidPath(Exception):
    """
    User provides an invalid fully-defined path
    """


# manager exceptions
class OperationFailure(Exception):
    """
    A multi-provider operation had some failure, but was not fatal
    Must contain the result of the operation, and the list of failures
    Raised only by read operations - any failure in a write operation will be fatal
    result should only be None if the original operation wasn't supposed to return anything
    (this only happens when the operation updates a cache)
    failures - a list of ProviderFailures
    """
    def __init__(self, failures, result):
        self.failures = failures
        self.result = result


class FatalOperationFailure(Exception):
    """
    A multi-provider operation had some failure that was fatal
    failures - a list of ProviderFailures
    """
    def __init__(self, failures):
        self.failures = failures

    def __str__(self):
        return str(map(str, self.failures))


class ReadOnlyMode(Exception):
    """
    Thrown when the system is in readonly mode because some providers are missing
    """
