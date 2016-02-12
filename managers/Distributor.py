from custom_exceptions import exceptions
from tools import encryption, erasure_encoding
import itertools

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

    def _recover(self, shares, key):
        """
        Returns:
            (result, bad_shares)
            result: A byte representation of the reconstructed message if the reconstruction was successful.
            bad_shares: the shares that were deemed cheaters
        """
        def attempt_recovery(shares):
            try:
                ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
                data = encryption.decrypt(ciphertext, key)
                return data
            except (exceptions.DecodeError, exceptions.DecryptError):
                return None

        def find_minimal_working_set():
            """
            Find some share set of size threshold that is recoverable
            Returns:
                (data, minimal_set)
                data: the recovered result
                minimal_set: the minimal share set
            Returns None if no such set exists
            """
            minimal_sets = itertools.combinations(shares, self.file_reconstruction_threshold)
            for test_set in minimal_sets:
                test_set = list(test_set)
                data = attempt_recovery(test_set)
                if data:
                    return data, test_set
            return None, None

        bad_shares = []

        # check 2 subgroups; threshold > n/2
        data = attempt_recovery(shares[:self.file_reconstruction_threshold])
        if data is not None and \
           data == attempt_recovery(shares[-self.file_reconstruction_threshold:]):
            return data, bad_shares

        # there was definitely some error; find a minimal working set
        if data is not None:
            minimal_working_set = shares[:self.file_reconstruction_threshold]
        else:
            data, minimal_working_set = find_minimal_working_set()
        if minimal_working_set is None:
            # cannot recover
            return None, bad_shares

        # substitute in other shares to find problematic ones
        for share in shares:
            if share in minimal_working_set:
                continue
            test_set = minimal_working_set[:-1] + [share]
            if attempt_recovery(test_set) != data:
                bad_shares.append(share)

        return data, bad_shares

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

        # map from share to provider returning that share
        shares_map = {}
        failures = []
        for provider in self.providers:
            try:
                shares_map[provider.get(filename)] = provider
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)

        shares = shares_map.keys()
        data, bad_shares = self._recover(shares, key)

        for bad_share in bad_shares:
            failures.append(exceptions.InvalidShareFailure(shares_map[bad_share]))

        if data is None:
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
