# general exceptions
class IllegalStateException(Exception):
    '''
    Indicates that a piece of logic should never have been reached
    '''


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


# manifest exceptions
class IllegalArgumentException(Exception):
    '''
    Passed too many or too few arguments to a constructor
    '''


class ParseException(Exception):
    '''
    Argument provided could not be parsed by the relevant regex
    '''
    pass


class FileNotFound(Exception):
    '''
    User requests a file by name that cannot be located in the manifest
    '''
    pass


# provider exceptions
class ConnectionFailure(Exception):
    '''
    Provider is considered off-line
    '''
    pass


class AuthFailure(Exception):
    '''
    Failed to authenticate the API token with the provider
    '''
    pass


class OperationFailure(Exception):
    '''
    The provider rejected the desired operation (reason unknown)
    '''
    pass
