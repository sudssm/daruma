from custom_exceptions import exceptions
from crypto import encryption, erasure_encoding

# For RS distributing files
# TODO make resistant to provider going down and other error cases


class FileDistributor:
    def __init__(self, providers, file_reconstruction_threshold):
        self.providers = providers
        self.num_providers = len(providers)
        self.file_reconstruction_threshold = file_reconstruction_threshold

    def put(self, filename, data, key=None):
        '''
        Args:
            filename: string
            data: bytestring
        Returns:
            tuple: (key, reached_threshold, failed_providers_map)
            key: bytestring of the key used for encryption
            reached_threshold = boolean
            failed_providers_map = failed provider mapped to its error code
                TODO: define provider error codes
        Raises:
            UnknownError, IllegalArugmentError from erasure_encoding.share
        '''
        # encrypt
        if key is None:
            key = encryption.generate_key()
        ciphertext = encryption.encrypt(data, key)

        # compute RS
        shares = erasure_encoding.share(ciphertext, self.file_reconstruction_threshold, self.num_providers)

        # upload to each provider
        failed_providers_map = {}
        for provider, share in zip(self.providers, shares):
            try:
                provider.put(filename, share)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.RejectedOperationFailure) as e:
                failed_providers_map[provider] = str(e)

        reached_threshold = (len(self.providers) - len(failed_providers_map)) <= self.file_reconstruction_threshold

        return (key, reached_threshold, failed_providers_map)

    def get(self, filename, key):
        '''
        Args:
        Returns:
        Raises:
        '''
        def get_share(provider):
            try:
                return provider.get(filename)
            except exceptions.ProviderFileNotFound:
                return None
            # TODO except other things?

        # download shares
        shares = [get_share(provider) for provider in self.providers]
        shares = [share for share in shares if share is not None]
        if len(shares) == 0:
            # no shares found - assume file doesn't exist
            raise exceptions.FileNotFound

        # TODO: address the case where some providers don't return shares?

        # un RS
        ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
        # decrypt
        data = encryption.decrypt(ciphertext, key)  # TODO: deal with failed auth

        return data

    def delete(self, filename):
        for provider in self.providers:
            try:
                provider.delete(filename)
            except exceptions.ProviderFileNotFound:
                pass
