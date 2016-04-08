# This file handles keys using SSSS
from tools import shamir_secret_sharing
from tools.encryption import KEY_SIZE
from tools.utils import FILENAME_SIZE
from collections import defaultdict
from custom_exceptions import exceptions
from itertools import product
import struct
import zlib


class Bootstrap:
    """
    A class to contain the Shamir-Shared data
    Contains the master key, manifest name, and file reconstruction threshold
    """

    # network-endian, string, string, int
    STRUCT_FORMAT = "!" + str(KEY_SIZE) + "s" + str(FILENAME_SIZE) + "si"
    SIZE = struct.calcsize(STRUCT_FORMAT)

    def __init__(self, key, manifest_name, file_reconstruction_threshold):
        self.key = str(key)
        self.manifest_name = str(manifest_name)
        self.file_reconstruction_threshold = file_reconstruction_threshold

    def __str__(self):
        return struct.pack(self.STRUCT_FORMAT, self.key, self.manifest_name, self.file_reconstruction_threshold)

    def __eq__(self, other):
        return other is not None and \
               self.key == other.key and self.manifest_name == other.manifest_name and \
               self.file_reconstruction_threshold == other.file_reconstruction_threshold

    @staticmethod
    def parse(string):
        key, manifest_name, file_reconstruction_threshold = struct.unpack(Bootstrap.STRUCT_FORMAT, string)
        return Bootstrap(key, manifest_name, file_reconstruction_threshold)


class BootstrapManager:
    BOOTSTRAP_FILE_NAME = "mellon"
    BOOTSTRAP_PLAINTEXT_FILE_NAME = "outjokeside"

    def __init__(self, providers, bootstrap_reconstruction_threshold=None):
        self.providers = providers
        self.bootstrap_reconstruction_threshold = bootstrap_reconstruction_threshold
        self.n = None

    def _determine_parameters(self, vote_map, failures):
        '''
        Determines the values for n and threshold, adding exceptions for providers who misvoted to the failures list
        Args:
            vote_map, maps (threshold, n) vote to providers that voted
            failures, a growing list of exceptions for failed providers
        Returns:
            (threshold, n)
            threshold: the voted bootstrap threshold
            n: the voted n
        '''
        # vote on threshold
        largest_group_size = 0
        winning_vote = None
        for vote, sources in vote_map.items():
            if len(sources) > largest_group_size:
                winning_vote = vote
                largest_group_size = len(sources)

        if winning_vote is not None:
            threshold, n = winning_vote

        # we protect against (k-1) providers failing
        # so, a group of defectors larger than k are outside threat model
        # just ensure that the largest group is size at least k
        if winning_vote is None or largest_group_size < threshold:
            raise exceptions.FatalOperationFailure(failures)

        # add all providers who misvoted to failures
        for vote, sources in vote_map.items():
            if vote != winning_vote:
                failures += [exceptions.InvalidShareFailure(provider) for provider in sources]

        return threshold, n

    def _download_and_vote(self):
        """
        Recovers n, bootstrap threshold and shares from providers if there is a consensus
        Returns:
            threshold, the voted bootstrap threshold
            n, the voted n
            provider_id_map, a map from id to list of providers who claim to have that id
            shares_map, a map from provider to its share
            failures, a list of failures from failing providers
        Raises FatalOperationFailure if unable to reach consensus
        """
        # maps self-proclaimed provider_id to providers with that id
        # (there could be multiple providers that report the same one)
        provider_id_map = defaultdict(list)
        shares_map = {}  # maps provider to bootstrap share
        vote_map = defaultdict(list)  # maps (threshold, n) vote to providers that voted

        failures = []
        for provider in self.providers:
            try:
                threshold_vote, n_vote, provider_id = provider.get(self.BOOTSTRAP_PLAINTEXT_FILE_NAME).split(",", 3)

                # track provider votes for bootstrap threshold and n values
                vote_map[(int(threshold_vote), int(n_vote))].append(provider)
                provider_id_map[provider_id].append(provider)

                shares_map[provider] = zlib.decompress(provider.get(self.BOOTSTRAP_FILE_NAME))
            except exceptions.ProviderFailure as e:
                failures.append(e)
            except (zlib.error, ValueError):
                # if the cast to int, decompressing or unpacking failed
                failures.append(exceptions.InvalidShareFailure(provider))

        threshold, n = self._determine_parameters(vote_map, failures)

        # add all providers with invalid id to failures
        for provider_id, providers in provider_id_map.items():
            try:
                provider_id = int(provider_id)
                assert provider_id < n and provider_id >= 0
            except (AssertionError, ValueError):
                for provider in providers:
                    failures.append(exceptions.InvalidShareFailure(provider))
                    # remove the provider's share from shares_map
                    del shares_map[provider]

        # ensure that we have at least threshold shares
        if len(shares_map.values()) < threshold:
            raise exceptions.FatalOperationFailure(failures)

        return threshold, n, provider_id_map, shares_map, failures

    def _reconstruct_shares(self, provider_id_map, shares_map):
        """
        Apply RSS to a share_map
        Args:
            provider_id_map, a map from provider id to list of providers who claim to hold that id
            shares_map, a map from provider to its share
        Returns:
            secret, the recovered secret
            failures, a list of exceptions from failing providers
        Raises:
            FatalOperationFailure if unable to reconstruct
        """
        # build a list of lists of (id, share) such that all shares with the same id are in the same list
        shares_lists = [[(provider_id, shares_map[provider]) for provider in providers if provider in shares_map]
                        for (provider_id, providers) in provider_id_map.items()]

        shares_lists = filter(lambda l: len(l) > 0, shares_lists)

        # select one share for each provider_id; build all such selections
        share_sets = product(*shares_lists)

        secret = None
        # find the first of share_sets that work
        for share_set in share_sets:
            share_set_map = {provider_id: share for (provider_id, share) in share_set}
            try:
                secret, good_ids, bad_ids = shamir_secret_sharing.reconstruct(share_set_map, Bootstrap.SIZE, self.n, self.bootstrap_reconstruction_threshold)
                break
            except exceptions.ReconstructionError:
                pass

        if secret is None:
            # None of them worked
            raise exceptions.FatalOperationFailure([])

        # we successfully found a working set
        bad_providers = []

        # handle all shares with an id that appeared in good_ids
        for good_id in good_ids:
            for provider in provider_id_map[good_id]:
                # there is no uncertainty about this share; don't test again
                del shares_map[provider]

        # handle the shares that were marked bad by reconstruction
        for bad_id in bad_ids:
            for provider in provider_id_map[bad_id]:
                # if this was the provider whose share went into reconstruct
                if shares_map[provider] == share_set_map[bad_id]:
                    bad_providers.append(provider)
                    del shares_map[provider]

                    break

        # try all remaining shares in this group one at a time
        good_share_map = {provider_id: share_set_map[provider_id] for provider_id in good_ids}
        test_shares = [(provider_id, provider, shares_map[provider]) for (provider_id, providers) in provider_id_map.items()
                       for provider in providers if provider in shares_map]

        for (provider_id, provider, share) in test_shares:
            good_share_map[provider_id] = share
            if not shamir_secret_sharing.verify(good_share_map, secret, self.n):
                bad_providers.append(provider)
            del good_share_map[provider_id]

        failures = [exceptions.InvalidShareFailure(provider) for provider in bad_providers]

        return secret, failures

    def recover_bootstrap(self):
        """
        Returns a Bootstrap object, collected from self.Providers
        Raises FatalOperationFailure or OperationFailure
        """
        self.bootstrap_reconstruction_threshold, self.n, \
            provider_id_map, shares_map, failures = self._download_and_vote()

        try:
            secret, shamir_failures = self._reconstruct_shares(provider_id_map, shares_map)
        except exceptions.FatalOperationFailure as e:
            failures.append(e)
            raise exceptions.FatalOperationFailure(failures)

        failures += shamir_failures

        bootstrap = Bootstrap.parse(secret)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, bootstrap)

        return bootstrap

    def distribute_bootstrap(self, bootstrap):
        """
        Secret-Share distribute a Bootstrap object to all providers
        """
        if self.n is None:
            # we are initializing the system (we haven't loaded a bootstrap before)
            self.n = len(self.providers)

        # TODO if self.n > len(self.providers), raise because we are in readonly?

        string = str(bootstrap)

        provider_ids = map(str, xrange(len(self.providers)))

        # compute new shares using len(providers) and bootstrap_reconstruction_threshold
        shares_map = shamir_secret_sharing.share(string, provider_ids, self.bootstrap_reconstruction_threshold)

        try:
            for key, share in shares_map.items():
                shares_map[key] = zlib.compress(share)
        except zlib.error:
            raise exceptions.LibraryException

        # write shares to providers
        failures = []
        for provider, provider_id in zip(self.providers, provider_ids):
            share = shares_map[provider_id]
            try:
                bootstrap_plaintext = ",".join(map(str, [self.bootstrap_reconstruction_threshold, self.n, provider_id]))
                provider.put(self.BOOTSTRAP_PLAINTEXT_FILE_NAME, bootstrap_plaintext)
                provider.put(self.BOOTSTRAP_FILE_NAME, share)
            except exceptions.ProviderFailure as e:
                failures.append(e)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
