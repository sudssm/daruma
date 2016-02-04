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
        """
        Args:
            filename: string
            data: bytestring
            key: an optional key used to encrypt
        Returns:
            tuple: (key, failures)
            key: bytestring of the key used for encryption
            failures: list of failures
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
            except (exceptions.ConnectionFailure, exceptions.OperationFailure) as e:
                failures.append(e)

        return (key, failures)

    def get(self, filename, key):
        """
        Args:
            filename: string
            key: bytestring
        Returns:
            result: bytestring or None if error
            failures: map of provider to error
        Raises:
             FileReconstructionError
        """
        def get_share(provider):
            return provider.get(filename)

        shares_map = {}
        failures = []
        for provider in self.providers:
            try:
                shares_map[provider] = get_share(provider)
            except (exceptions.ConnectionFailure, exceptions.OperationFailure) as e:
                failures.append(e)

        shares = shares_map.values()
        if len(shares) < self.file_reconstruction_threshold:
            return (None, failures)

        # TODO handle RS differently
        # If we can recover but have some cheating shares, we treat them as failures
        # If we can't recover at all, this should throw an exception
        # decode Reed Solomon
        try:
            ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
            # decrypt
            data = encryption.decrypt(ciphertext, key)
        except (exceptions.DecodeError, exceptions.DecryptError):
            raise exceptions.FileReconstructionError

        return (data, failures)

    def delete(self, filename):
        for provider in self.providers:
            try:
                provider.delete(filename)
            except (exceptions.ConnectionFailure, exceptions.OperationFailure):
                pass
