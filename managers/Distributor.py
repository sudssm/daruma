from custom_exceptions import exceptions
from crypto import encryption, erasure_encoding

# For RS distributing files
# TODO make resistant to provider going down and other error cases


class FileDistributor:
    def __init__(self, providers, file_reconstruction_threshold):
        if file_reconstruction_threshold > providers:
            raise exceptions.IllegalArgumentError

        self.providers = providers
        self.num_providers = len(providers)
        self.file_reconstruction_threshold = file_reconstruction_threshold

    def put(self, filename, data, key=None):
        """
        Args:
            filename: string
            data: bytestring
            key: an optional key used to encrypt
        Returns:
            tuple: (key, failed_providers_map)
            key: bytestring of the key used for encryption
            failed_providers_map: failed provider mapped to exception
        """
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
                failed_providers_map[provider] = e

        return (key, failed_providers_map)

    def get(self, filename, key):
        """
        Args:
            filename: string
            key: bytestring
        Returns:
            result: bytestring or None if error
            failed_providers_map: map of provider to error
        Raises:
             DecodeError, DecryptError from erasure_encoding.reconstruct, encryption.decrypt
        """
        def get_share(provider):
            return provider.get(filename)

        shares_map = {}
        failures_map = {}
        for provider in self.providers:
            try:
                shares_map[provider] = get_share(provider)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure) as e:
                failures_map[provider] = e

        shares = shares_map.values()
        if len(shares) < self.file_reconstruction_threshold:
            return (None, failures_map)

        # TODO handle RS differently
        # If we can recover but have some cheating shares, we treat them as failures
        # If we can't recover at all, this should throw an exception
        # decode Reed Solomon
        ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
        # decrypt
        data = encryption.decrypt(ciphertext, key)

        return (data, failures_map)

    def delete(self, filename):
        for provider in self.providers:
            try:
                provider.delete(filename)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure):
                pass
