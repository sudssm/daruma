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
            reached_threshold: boolean
            failed_providers_map: failed provider mapped to its error code
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
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure) as e:
                failed_providers_map[provider] = str(e)

        reached_threshold = (len(self.providers) - len(failed_providers_map)) <= self.file_reconstruction_threshold

        return (key, reached_threshold, failed_providers_map)

    def get(self, filename, key):
        '''
        Args:
            filename: string
            key: bytestring
        Returns:
            result: bytestring or None (None = too many failed)
            failed_providers_map: failed provider mapped to its error code
                TODO: define provider error codes
        Raises:
             DecodeError, DecryptError from erasure_encoding.reconstruct, encryption.decrypt
        '''
        def get_share(provider):
            '''
            Args:
            Returns:
                tuple (result, provider, status)
                result: content of the file share or None if no share is returned
                provider: the provider used in a given call
                status: the error code returned by the provider call or None on success
            '''
            try:
                return (provider.get(filename), provider, None)
                # TODO: do we want something other than None for success?
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure) as e:
                return (None, provider, str(e))

        # download shares
        tuples = [get_share(provider) for provider in self.providers]
        shares_map = {tup[1]: tup[0] for tup in tuples if tup[0] is not None and tup[2] is None}
        failures_map = {tup[1]: tup[2] for tup in tuples if tup[0] is None and tup[2] is not None}

        if (len(failures_map) + len(shares_map) != len(self.providers)):
            raise exceptions.IllegalStateException

        if (len(shares_map) < self.file_reconstruction_threshold):
            return (None, failures_map)

        # decode Reed Solomon
        ciphertext = erasure_encoding.reconstruct(shares_map.values(), self.file_reconstruction_threshold, self.num_providers)
        # decrypt
        data = encryption.decrypt(ciphertext, key)

        return (data, failures_map)

    def delete(self, filename):
        for provider in self.providers:
            try:
                provider.delete(filename)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure):
                pass  # TODO: what do we want to do here?
