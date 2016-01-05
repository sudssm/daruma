# This file handles keys using SSSS
import crypto.shamir_secret_sharing
from crypto.encryption import generate_key
from providers.BaseProvider import ProviderFileNotFound

class KeyManager:
    KEY_FILE_NAME = "mellon"

    def __init__(self, providers, k_key):
        self.providers = providers
        self.k = k_key

    # un SSSS the key from the providers
    # returns the recovered key from all the shares
    # throws ProvidersUnconfigured if no provider has a keyshare
    # throws ProvidersDown if not enough providers have keyshares
    # probably should throw some sort of connection exception too
    def recover_key(self):
        def get_share(provider):
            try:
                return provider.get(self.KEY_FILE_NAME)
            except ProviderFileNotFound:
                return None
        # get all shares from providers in parallel
        shares_map = {}
        for provider in self.providers:
            shares_map[provider] = get_share(provider)
        shares = [value for value in shares_map.values() if value is not None]
        if len(shares) < self.k:
            raise Exception
            #return None  # TODO: return error condition to indicate that there are too few shares to reconstruct key

        # attempt to recover key
        secret_key = crypto.shamir_secret_sharing.reconstruct(shares)

        success = True
        # if there were providers that had invalid or missing shares
        if len(shares) < len(self.providers):
            success = False
            # TODO do some fixing stuff here? someone got corrupted

        return secret_key

    # distributes a new key to all providers
    # probably throws exception if the provider's put method fails
    def distribute_key(self):
        key = generate_key()

        # compute new shares using len(providers) and k_key
        shares = crypto.shamir_secret_sharing.share(key, self.k, len(self.providers))

        # write shares to providers
        for provider, share in zip(self.providers, shares):
            provider.put(self.KEY_FILE_NAME, share)

        return key