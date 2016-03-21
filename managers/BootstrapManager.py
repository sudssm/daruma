# This file handles keys using SSSS
import tools.shamir_secret_sharing
from tools.encryption import KEY_SIZE
from tools.utils import FILENAME_SIZE, generate_random_name
from collections import defaultdict
import struct
from custom_exceptions import exceptions


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

    def recover_bootstrap(self):
        """
        Returns a Bootstrap object, collected from self.Providers
        Raises FatalOperationFailure or OperationFailure
        """
        # maps self-proclaimed provider_id to provider
        provider_id_map = {}
        # maps provider_id to bootstrap share
        shares_map = {}
        # maps threshold vote to providers that voted
        thresholds_map = defaultdict(list)
        failures = []
        for provider in self.providers:
            try:
                threshold_vote, provider_id = provider.get(self.BOOTSTRAP_PLAINTEXT_FILE_NAME).split(",")
                # track provider votes for bootstrap threshold values
                thresholds_map[int(threshold_vote)].append(provider)

                provider_id_map[provider_id] = provider
                shares_map[provider_id] = provider.get(self.BOOTSTRAP_FILE_NAME)
            except exceptions.ProviderFailure as e:
                failures.append(e)
            except ValueError:
                # if the cast to int or unpacking failed
                failures.append(exceptions.InvalidShareFailure(provider))

        # vote on threshold
        largest_group_size = 0
        threshold = None
        for threshold_vote, sources in thresholds_map.items():
            if len(sources) > largest_group_size:
                threshold = threshold_vote
                largest_group_size = len(sources)

        # we protect against (k-1) providers failing
        # so, a group of defectors larger than k are outside threat model
        # just ensure that the largest group is size larger than k
        if threshold is None or largest_group_size < threshold:
            raise exceptions.FatalOperationFailure(failures)

        self.bootstrap_reconstruction_threshold = threshold

        # add all providers who misvoted to failures
        for threshold_vote, sources in thresholds_map.items():
            if threshold_vote != self.bootstrap_reconstruction_threshold:
                failures += [exceptions.InvalidShareFailure(provider) for provider in sources]

        # reconstruct shares
        shares = shares_map.values()
        if len(shares) < self.bootstrap_reconstruction_threshold:
            raise exceptions.FatalOperationFailure(failures)

        # attempt to recover key
        # TODO find cheaters - just pass in the entire map
        try:
            string = tools.shamir_secret_sharing.reconstruct(shares, Bootstrap.SIZE, len(self.providers))
            bootstrap = Bootstrap.parse(string)
        except exceptions.LibraryException:  # TODO: update when RSS is introduced
            raise exceptions.FatalOperationFailure(failures)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, bootstrap)

        return bootstrap

    def distribute_bootstrap(self, bootstrap):
        """
        Secret-Share distribute a Bootstrap object to all providers
        """
        string = str(bootstrap)

        provider_ids = [generate_random_name() for provider in self.providers]

        # TODO pass in provider_ids to robust when RSS done
        # compute new shares using len(providers) and bootstrap_reconstruction_threshold
        shares = tools.shamir_secret_sharing.share(string, self.bootstrap_reconstruction_threshold, len(self.providers))

        # write shares to providers
        failures = []
        for provider, provider_id, share in zip(self.providers, provider_ids, shares):
            try:
                bootstrap_plaintext = str(self.bootstrap_reconstruction_threshold) + "," + provider_id
                provider.put(self.BOOTSTRAP_PLAINTEXT_FILE_NAME, bootstrap_plaintext)
                provider.put(self.BOOTSTRAP_FILE_NAME, share)
            except exceptions.ProviderFailure as e:
                failures.append(e)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
