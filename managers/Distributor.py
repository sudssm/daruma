from custom_exceptions import exceptions
from tools import encryption, erasure_encoding
from tools.utils import run_parallel
import itertools

# For RS distributing files


class FileDistributor:
    """
    A system for distributing files for a specific set of providers and threshold
    If a different set of providers and threshold is needed, a new FileDistributor
    object should be constructed
    """
    def __init__(self, providers, num_providers, file_reconstruction_threshold):
        """
        Create a FileDistributor
        Args:
            providers: a list of providers to use
            num_providers: the total number of providers that have been configured with this system before
            file_reconstruction_threshold: the threshold for file file_reconstruction_threshold
        """
        # make a copy of the provider list
        self.providers = providers[:]
        self.num_providers = num_providers
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
        def upload(provider, share):
            provider.put(filename, share)

        failures = run_parallel(upload, zip(self.providers, shares))

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)

        return key

    def _recover(self, shares, key):
        """
        Returns:
            (result, bad_shares)
            result: A byte representation of the reconstructed message if the reconstruction was successful, or None otherwise
            bad_shares: the shares that were deemed cheaters
        """
        def attempt_recovery(shares):
            ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
            data = encryption.decrypt(ciphertext, key)
            return data

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
                try:
                    data = attempt_recovery(test_set)
                    return data, test_set
                except (exceptions.DecodeError, exceptions.DecryptError):
                    # continue searching
                    pass
            return None, None

        bad_shares = []

        # split shares into groups of size threshold
        groups = zip(*[iter(shares)]*self.file_reconstruction_threshold)

        # if not all shares made it (threshold doesn't divide n), also test the last (threshold) shares
        if len(groups) * self.file_reconstruction_threshold < len(shares):
            groups.append(shares[-self.file_reconstruction_threshold:])

        data = None
        try:
            # test all groups, make sure they all return the same thing
            data = attempt_recovery(groups[0])
            for group in groups[1:]:
                assert data == attempt_recovery(group)
        except (AssertionError, exceptions.DecodeError, exceptions.DecryptError):
            # there was definitely some error; find a minimal working set
            if data is not None:
                minimal_working_set = groups[0]
            else:
                data, minimal_working_set = find_minimal_working_set()
            if minimal_working_set is None:
                # cannot recover
                return None, bad_shares

            # substitute in other shares to find problematic ones
            test_set = minimal_working_set
            for share in shares:
                if share in minimal_working_set:
                    continue
                test_set[-1] = share
                try:
                    if attempt_recovery(test_set) != data:
                        bad_shares.append(share)
                except (exceptions.DecodeError, exceptions.DecryptError):
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

        def get_share(provider):
            shares_map[provider.get(filename)] = provider

        args = map(lambda provider: [provider], self.providers)
        failures = run_parallel(get_share, args)

        shares = shares_map.keys()

        if len(shares) < self.file_reconstruction_threshold:
            raise exceptions.FatalOperationFailure(failures)

        data, bad_shares = self._recover(shares, key)

        for bad_share in bad_shares:
            failures.append(exceptions.InvalidShareFailure(shares_map[bad_share]))

        if data is None:
            raise exceptions.FatalOperationFailure(failures)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, data)

        return data

    def delete(self, filename):
        def delete_share(provider):
            provider.delete(filename)
        args = map(lambda provider: [provider], self.providers)
        failures = run_parallel(delete_share, args)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
