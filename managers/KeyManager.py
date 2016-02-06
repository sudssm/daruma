# This file handles keys using SSSS
import tools.shamir_secret_sharing
import tools.encryption
import tools.utils
from custom_exceptions import exceptions


class KeyManager:
    KEY_FILE_NAME = "mellon"

    def __init__(self, providers, key_reconstruction_threshold):
        self.providers = providers
        self.key_reconstruction_threshold = key_reconstruction_threshold

    # un SSSS the key from the providers
    # returns the recovered key from all the shares
    # throws ProvidersUnconfigured if no provider has a keyshare
    # throws ProvidersDown if not enough providers have keyshares
    # probably should throw some sort of connection exception too
    def recover_key_and_name(self):
        def get_share(provider):
            return provider.get(self.KEY_FILE_NAME)

        shares_map = {}
        failures = []
        for provider in self.providers:
            try:
                shares_map[provider] = get_share(provider)
            except (exceptions.ConnectionFailure, exceptions.OperationFailure) as e:
                failures.append(e)

        # TODO handle failures

        shares = shares_map.values()
        if len(shares) < self.key_reconstruction_threshold:
            raise exceptions.KeyReconstructionError

        # attempt to recover key
        try:
            plaintext = tools.shamir_secret_sharing.reconstruct(shares)
            name = plaintext[0:tools.utils.FILENAME_SIZE]
            key = plaintext[-tools.encryption.KEY_SIZE:]

        except exceptions.DecodeError:
            raise exceptions.KeyReconstructionError

        return key, name

    # distributes a new key and name to all providers
    # probably throws exception if the provider's put method fails
    def distribute_key_and_name(self, key, name):
        # concatenate them together; both lengths are fixed
        plaintext = name + key

        # compute new shares using len(providers) and key_reconstruction_threshold
        shares = tools.shamir_secret_sharing.share(plaintext, self.key_reconstruction_threshold, len(self.providers))

        # write shares to providers
        failures = []
        for provider, share in zip(self.providers, shares):
            try:
                provider.put(self.KEY_FILE_NAME, share)
            except (exceptions.ConnectionFailure, exceptions.OperationFailure) as e:
                failures.append(e)

        # TODO handle failures
        # TODO re-handle manifest
