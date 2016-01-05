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

# distributor exceptions 
class ProvidersDown(Exception):
    pass
class ProvidersUnconfigured(Exception):
    pass
class FileNotFound(Exception):
    pass

# manifest exceptions
class InvalidFormatException(Exception):
    pass
class IllegalArgumentException(Exception):
    pass


# provider exceptions
class ProviderFileNotFound(EnvironmentError):
    pass
class ProviderConnectionError(EnvironmentError):
    pass
