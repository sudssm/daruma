# This file handles keys using SSSS
from tools import shamir_secret_sharing
from tools.encryption import KEY_SIZE
from tools.utils import FILENAME_SIZE, run_parallel, generate_random_name
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
        self.num_providers = None

    def _make_bootstrap_plaintext(self, threshold, n, provider_id, version):
        return ",".join(map(str, [threshold, n, provider_id, version]))

    def _parse_bootstrap_plaintext(self, plaintext):
        return plaintext.split(",", 4)

    def _download_and_vote(self):
        """
        Recovers n, bootstrap threshold, shares, and failures from providers if there is a consensus
        A provider may be considered failing when one of the following cases is met:
            a provider experiences some error that prevents a returned share
            a provider gives a share with structoral errors (wrong type, cannot decompress or unpack, etc)
            the provider does not vote for the consensus n, bootstrap threshold
            a provider id is of the wrong type or out of the predetermined range
        Returns:
            threshold, the voted bootstrap threshold
            n, the voted n
            provider_id_map, a map from id to list of providers who claim to have that id
            shares_map, a map from provider to its share
            failures, a list of failures from failing providers
        Raises FatalOperationFailure if unable to reach consensus
        """
        def vote_for_params(vote_map):
            """
            Args:
                vote_map: maps tuple of (threshold, n, version) votes to providers that voted
            Returns:
                (threshold, n), failures
                threshold: the voted bootstrap threshold
                n: the voted n
                failed_providers: a list of providers who did not vote for the winning vote if one was found
            Raises:
                FatalOperationFailure: no parameters were returned or there were too few providers in agreement to support the consensus threshold
            """
            # vote on threshold
            largest_group_size = 0
            winning_vote = None
            for vote, sources in vote_map.items():
                if len(sources) > largest_group_size:
                    winning_vote = vote
                    largest_group_size = len(sources)

            if winning_vote is not None:
                threshold, n, version = winning_vote

            # we protect against (k-1) providers failing
            # so, a group of defectors larger than k are outside threat model
            # just ensure that the largest group is size at least k
            if winning_vote is None or largest_group_size < threshold:
                raise exceptions.FatalOperationFailure([], "didn't reach bootstrap vote consensus")

            failed_providers = []
            # add all providers who misvoted to failures
            for vote, sources in vote_map.items():
                if vote != winning_vote:
                    failed_providers += sources

            return threshold, n, failed_providers

        provider_id_map = defaultdict(list)
        shares_map = {}  # maps provider to bootstrap share
        vote_map = defaultdict(list)  # maps (threshold, n) vote to providers that voted

        def get_bootstrap_plaintext(provider):
            try:
                bootstrap_plaintext = zlib.decompress(provider.get(self.BOOTSTRAP_PLAINTEXT_FILE_NAME))
                threshold_vote, n_vote, provider_id, version = self._parse_bootstrap_plaintext(bootstrap_plaintext)

                # track provider votes for bootstrap threshold, n values, and version
                vote_map[(int(threshold_vote), int(n_vote), version)].append(provider)
                provider_id_map[provider_id].append(provider)
            except ValueError:
                raise exceptions.InvalidShareFailure(provider, "Got invalid boostrap share from " + str(provider))

        def get_bootstrap_share(provider):
            try:
                shares_map[provider] = zlib.decompress(provider.get(self.BOOTSTRAP_FILE_NAME))
            except zlib.error:
                raise exceptions.InvalidShareFailure(provider)

        def run_on_provider(func, provider):
            return func(provider)

        args = []
        for provider in self.providers:
            args.append([get_bootstrap_plaintext, provider])
            args.append([get_bootstrap_share, provider])

        failures = run_parallel(run_on_provider, args)

        # we don't want to double penalize if a provider fails in the same way on both files
        failures = list(set(failures))

        try:
            threshold, n, voting_failures = vote_for_params(vote_map)
        except exceptions.FatalOperationFailure as e:
            raise exceptions.FatalOperationFailure(failures + e.failures)

        # add all providers with invalid id to failures
        for provider_id, providers in provider_id_map.items():
            try:
                provider_id = int(provider_id)
                assert provider_id < n and provider_id >= 0
            except (AssertionError, ValueError):
                for provider in providers:
                    failures.append(exceptions.InvalidShareFailure(provider))
                    # remove the provider's share from shares_map
                    shares_map.pop(provider, None)

        # if a provider misvoted, don't use its share - delete it if it hasn't been deleted already
        for provider in voting_failures:
            shares_map.pop(provider, None)

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
                secret, good_ids, bad_ids = shamir_secret_sharing.reconstruct(share_set_map, Bootstrap.SIZE, self.num_providers, self.bootstrap_reconstruction_threshold)
                break
            except exceptions.ReconstructionError:
                pass

        if secret is None:
            # None of them worked
            raise exceptions.FatalOperationFailure([], "could not recover a secret")

        # we successfully found a working set
        bad_providers = []

        # handle all shares with an id that appeared in good_ids
        for good_id in good_ids:
            for provider in provider_id_map[good_id]:
                # there is no uncertainty about this share; don't test again
                shares_map.pop(provider, None)

        # handle the shares that were marked bad by reconstruction
        for bad_id in bad_ids:
            for provider in provider_id_map[bad_id]:
                # if this was the provider whose share went into reconstruct
                if shares_map[provider] == share_set_map[bad_id]:
                    bad_providers.append(provider)
                    shares_map.pop(provider, None)

                    break

        # try all remaining shares in this group one at a time
        good_share_map = {provider_id: share_set_map[provider_id] for provider_id in good_ids}
        test_shares = [(provider_id, provider, shares_map[provider]) for (provider_id, providers) in provider_id_map.items()
                       for provider in providers if provider in shares_map]

        for (provider_id, provider, share) in test_shares:
            good_share_map[provider_id] = share
            if not shamir_secret_sharing.verify(good_share_map, secret, self.num_providers):
                bad_providers.append(provider)
            good_share_map.pop(provider_id, None)

        failures = [exceptions.InvalidShareFailure(provider) for provider in bad_providers]

        return secret, failures

    def recover_bootstrap(self):
        """
        Returns boostrap, num_providers:
            a Bootstrap object, and an integer number of providers collected from self.providers
        Raises FatalOperationFailure or OperationFailure with the same data
        """
        self.bootstrap_reconstruction_threshold, self.num_providers, \
            provider_id_map, shares_map, failures = self._download_and_vote()

        try:
            secret, shamir_failures = self._reconstruct_shares(provider_id_map, shares_map)
        except exceptions.FatalOperationFailure as e:
            raise exceptions.FatalOperationFailure(failures + e.failures, "could not recover bootstrap")

        failures += shamir_failures

        bootstrap = Bootstrap.parse(secret)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, (bootstrap, self.num_providers))

        return bootstrap, self.num_providers

    def distribute_bootstrap(self, bootstrap):
        """
        Secret-Share distribute a Bootstrap object to all providers
        """
        self.num_providers = len(self.providers)

        string = str(bootstrap)

        provider_ids = map(str, xrange(len(self.providers)))

        # make a random version
        version = generate_random_name()

        # compute new shares using len(providers) and bootstrap_reconstruction_threshold
        shares_map = shamir_secret_sharing.share(string, provider_ids, self.bootstrap_reconstruction_threshold)

        # write shares to providers
        def put_to_provider(provider, filename, data):
            provider.put(filename, data)

        args = []
        for provider, provider_id in zip(self.providers, provider_ids):
            share = shares_map[provider_id]
            bootstrap_plaintext = self._make_bootstrap_plaintext(self.bootstrap_reconstruction_threshold, self.num_providers, provider_id, version)

            args.append([provider, self.BOOTSTRAP_PLAINTEXT_FILE_NAME, zlib.compress(bootstrap_plaintext)])
            args.append([provider, self.BOOTSTRAP_FILE_NAME, zlib.compress(share)])

        failures = run_parallel(put_to_provider, args)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
