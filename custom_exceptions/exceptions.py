# crypto exceptions
class DecryptError(Exception):
    """
    Exception for errors in decryption and/or authentication
    """


class DecodeError(Exception):
    """
    Exception for errors in decoding an erasure code
    """


class SecretReconstructionError(Exception):
    """
    Exception for errors in decoding a secret
    """


# secretbox exceptions
class InvalidParametersException(Exception):
    '''
    Exception indicating that provided parameters will case
    secret sharing or erasure encoding to fail or be meaningless
    '''


# distributor exceptions
class ProvidersDown(Exception):
    pass


class ProvidersUnconfigured(Exception):
    pass


class ConnectionFailure(Exception):
    pass


class AuthFailure(Exception):
    pass


class RejectedOperationFailure(Exception):
    pass

# manifest exceptions
class IllegalArgumentException(Exception):
    pass


class ParseException(Exception):
    pass


class FileNotFound(Exception):
    pass


# provider exceptions
class ProviderFileNotFound(EnvironmentError):
    pass


class ProviderConnectionError(EnvironmentError):
    pass
