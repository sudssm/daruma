# This file handles keys using SSSS
import tools.shamir_secret_sharing
from tools.encryption import KEY_SIZE
from tools.utils import FILENAME_SIZE
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
    BOOTSTRAP_THRESHOLD_FILE_NAME = "outjokeside"

    def __init__(self, providers, bootstrap_reconstruction_threshold=None):
        self.providers = providers
        self.bootstrap_reconstruction_threshold = bootstrap_reconstruction_threshold

    def recover_bootstrap(self):
        """
        Returns a Bootstrap object, collected from self.Providers
        Raises FatalOperationFailure or OperationFailure
        """
        # maps provider to bootstrap share
        shares_map = {}
        # maps threshold vote to providers that voted
        thresholds_map = defaultdict(list)
        failures = []
        for provider in self.providers:
            try:
                shares_map[provider] = provider.get(self.BOOTSTRAP_FILE_NAME)
                # track provider votes for bootstrap threshold values
                thresholds_map[int(provider.get(self.BOOTSTRAP_THRESHOLD_FILE_NAME))].append(provider)
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)
            except ValueError:
                # if the cast to int failed
                failures.append(exceptions.IncorrectFileFailure(provider))

        # vote on threshold
        for threshold, sources in thresholds_map.items():
            if len(sources) > len(self.providers) / 2:
                self.bootstrap_reconstruction_threshold = threshold
            else:
                # add providers to failures
                for provider in sources:
                    failures.append(exceptions.IncorrectFileFailure(provider))

        # if still not set, we have a problem
        if self.bootstrap_reconstruction_threshold is None:
            raise exceptions.FatalOperationFailure(failures)

        shares = shares_map.values()
        if len(shares) < self.bootstrap_reconstruction_threshold:
            raise exceptions.FatalOperationFailure(failures)

        # attempt to recover key
        # TODO find cheaters
        try:
            string = tools.shamir_secret_sharing.reconstruct(shares)
            bootstrap = Bootstrap.parse(string)
        except exceptions.DecodeError:
            raise exceptions.FatalOperationFailure(failures)

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, bootstrap)

        return bootstrap

    def distribute_bootstrap(self, bootstrap):
        """
        Secret-Share distribute a Bootstrap object to all providers
        """
        string = str(bootstrap)

        # compute new shares using len(providers) and bootstrap_reconstruction_threshold
        shares = tools.shamir_secret_sharing.share(string, self.bootstrap_reconstruction_threshold, len(self.providers))

        # write shares to providers
        failures = []
        for provider, share in zip(self.providers, shares):
            try:
                provider.put(self.BOOTSTRAP_THRESHOLD_FILE_NAME, str(self.bootstrap_reconstruction_threshold))
                provider.put(self.BOOTSTRAP_FILE_NAME, share)
            except (exceptions.ConnectionFailure, exceptions.ProviderOperationFailure) as e:
                failures.append(e)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)
