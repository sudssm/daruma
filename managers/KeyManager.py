# This file handles keys using SSSS
import crypto.shamir_secret_sharing
from crypto.encryption import generate_key
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
    def recover_key(self):
        def get_share(provider):
            return provider.get(self.KEY_FILE_NAME)

        shares_map = {}
        failures_map = {}
        for provider in self.providers:
            try:
                shares_map[provider] = get_share(provider)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure) as e:
                failures_map[provider] = e

        shares = shares_map.values()
        if len(shares) < self.key_reconstruction_threshold:
            raise exceptions.KeyReconstructionError

        # attempt to recover key
        try:
            secret_key = crypto.shamir_secret_sharing.reconstruct(shares)
        except exceptions.DecodeError:
            raise exceptions.KeyReconstructionError

        return secret_key

    # distributes a new key to all providers
    # probably throws exception if the provider's put method fails
    def distribute_new_key(self):
        key = generate_key()

        # compute new shares using len(providers) and key_reconstruction_threshold
        shares = crypto.shamir_secret_sharing.share(key, self.key_reconstruction_threshold, len(self.providers))

        # write shares to providers
        failed_providers_map = {}
        for provider, share in zip(self.providers, shares):
            try:
                provider.put(self.KEY_FILE_NAME, share)
            except (exceptions.ConnectionFailure, exceptions.AuthFailure, exceptions.OperationFailure) as e:
                failed_providers_map[provider] = e

        # TODO handle failed providers map

        return key
