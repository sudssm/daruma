# This file handles keys using SSSS
import tools.shamir_secret_sharing
from tools.encryption import KEY_SIZE
from tools.utils import FILENAME_SIZE, generate_random_name
from collections import defaultdict
from custom_exceptions import exceptions
from itertools import product
import struct


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

    def _download_and_vote(self):
        """
        Recovers n, threshold and shares from providers if there is a consensus
        Returns:
            threshold, the voted threshold
            n, the voted n
            provider_id_map, a map from id to list of providers with that id
            shares_map, a map from provider to its share
            failures, a list of failures from failing providers
        Raises FatalOperationFailure if unable to reach consensus
        """
        # maps self-proclaimed provider_id to providers with that id
        # (there could be multiple providers that report the same one)
        provider_id_map = defaultdict(list)
        # maps provider to bootstrap share
        shares_map = {}
        # maps (threshold, n) vote to providers that voted
        vote_map = defaultdict(list)

        failures = []
        for provider in self.providers:
            try:
                threshold_vote, n_vote, provider_id = provider.get(self.BOOTSTRAP_PLAINTEXT_FILE_NAME).split(",", 3)

                # track provider votes for bootstrap threshold and n values
                vote_map[(int(threshold_vote), int(n_vote))].append(provider)
                provider_id_map[provider_id].append(provider)

                shares_map[provider] = provider.get(self.BOOTSTRAP_FILE_NAME)
            except exceptions.ProviderFailure as e:
                failures.append(e)
            except ValueError:
                # if the cast to int or unpacking failed
                failures.append(exceptions.InvalidShareFailure(provider))

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
        # just ensure that the largest group is size larger than k
        if winning_vote is None or largest_group_size < threshold:
            raise exceptions.FatalOperationFailure(failures)

        # add all providers who misvoted to failures
        for vote, sources in vote_map.items():
            if vote != winning_vote:
                failures += [exceptions.InvalidShareFailure(provider) for provider in sources]

        # ensure that we have at least threshold shares
        if len(shares_map.values()) < threshold:
            raise exceptions.FatalOperationFailure(failures)

        return threshold, n, provider_id_map, shares_map, failures

    def _reconstruct_shares(self, provider_id_map, shares_map):
        """
        Apply RSS to a share_map
        Args:
            provider_id_map, a map from provider id to list of providers with that id
            shares_map, a map from provider to its share
        Returns:
            secret, the recovered secret
            failures, a list of exceptions from failing providers
        Returns the recovered secret, and a list of exceptions from bad providers
        """
        # build a list of lists of shares with same id
        shares_lists = [[(provider_id, shares_map[provider]) for provider in providers if provider in shares_map]
                        for (provider_id, providers) in provider_id_map.items()]
        # select one share for each provider_id; build all such selections
        share_sets = product(*shares_lists)

        # only one of share_sets will work
        for share_set in share_sets:
            """
            to be filled in during integration
            try:
                robustrecover(...., share_set)
                # we found the working subset!
                # take the successful set, and mark all providers with overlapping ids as bad
                # also mark all providers in the bad set as bad
                # cycle in shares that are not elements of good or bad set to test one by one; mark bad ones bad
                # return stuff
            except Problem:
                continue
            """
            # TODO change when integrating rss
            shares = [share for (_, share) in share_set]
            failures = []

            try:
                string = tools.shamir_secret_sharing.reconstruct(shares, Bootstrap.SIZE, len(self.providers))
            except exceptions.LibraryException:
                raise exceptions.FatalOperationFailure(failures)

            return string, failures

        # none of them worked
        return None, []

    def recover_bootstrap(self):
        """
        Returns a Bootstrap object, collected from self.Providers
        Raises FatalOperationFailure or OperationFailure
        """
        self.bootstrap_reconstruction_threshold, self.n, \
            provider_id_map, shares_map, failures = self._download_and_vote()

        secret, shamir_failures = self._reconstruct_shares(provider_id_map, shares_map)
        failures += shamir_failures

        if secret is None:
            raise exceptions.FatalOperationFailure(failures)

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

        string = str(bootstrap)

        provider_ids = [generate_random_name() for provider in self.providers]

        # TODO pass in provider_ids to robust when RSS done
        # compute new shares using len(providers) and bootstrap_reconstruction_threshold
        shares = tools.shamir_secret_sharing.share(string, self.bootstrap_reconstruction_threshold, len(self.providers))

        # write shares to providers
        failures = []
        for provider, provider_id, share in zip(self.providers, provider_ids, shares):
            try:
                bootstrap_plaintext = ",".join([str(self.bootstrap_reconstruction_threshold), str(self.n), provider_id])
                provider.put(self.BOOTSTRAP_PLAINTEXT_FILE_NAME, bootstrap_plaintext)
                provider.put(self.BOOTSTRAP_FILE_NAME, share)
            except exceptions.ProviderFailure as e:
                failures.append(e)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
