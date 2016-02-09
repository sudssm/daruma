from custom_exceptions import exceptions
from tools import encryption, erasure_encoding

# For RS distributing files


class FileDistributor:
    def __init__(self, providers, file_reconstruction_threshold):
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
            key: bytestring of the key used for encryption
        Raises:
            FatalOperationFailure if any provider failed
        """
        # encrypt
        if key is None:
            key = encryption.generate_key()
        ciphertext = encryption.encrypt(data, key)

        # compute RS
        shares = erasure_encoding.share(ciphertext, self.file_reconstruction_threshold, self.num_providers)

        # upload to each provider
        failures = []
        for provider, share in zip(self.providers, shares):
            try:
                provider.put(filename, share)

            # pass up AuthFailure, get user to relogin.
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)

        return key

    def get(self, filename, key):
        """
        Args:
            filename: string
            key: bytestring
        Returns:
            result: bytestring
        Raises:
             FileReconstructionError
             OperationFailure if any provider failed
        """
        def get_share(provider):
            return provider.get(filename)

        shares_map = {}
        failures = []
        for provider in self.providers:
            try:
                shares_map[provider] = get_share(provider)
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)

        shares = shares_map.values()

        # TODO move this into RS lib
        if len(shares) < self.file_reconstruction_threshold:
            raise exceptions.FatalOperationFailure(failures)

        # TODO RS should identify broken shares
        try:
            ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
            # decrypt
            data = encryption.decrypt(ciphertext, key)
        except (exceptions.DecodeError, exceptions.DecryptError):
            # we could not recover the file
            raise exceptions.FatalOperationFailure(failures)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, data)

        return data

    def delete(self, filename):
        failures = []
        for provider in self.providers:
            try:
                provider.delete(filename)
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)
        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
