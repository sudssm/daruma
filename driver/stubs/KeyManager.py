# This file handles keys using SSSS
import algos.shamir_secret_sharing


class KeyManager:
    KEY_FILE_NAME = "the-name-of-our-key-file"

    def __init__(self, providers, k_key):
        self.providers = providers
        self.k_key = k_key

    # un SSSS the key from the providers
    # returns the recovered key from all the shares
    # throws ProvidersUnconfigured if no provider has a keyshare
    # throws ProvidersDown if not enough providers have keyshares
    # probably should throw some sort of connection exception too
    def recover_key(self):
        # get all shares from providers in parallel
        shares_map = {}
        for provider in self.provders:
            shares_map[provider] = None   # TODO: interface with providers -
                                          #  None only if no share or provider not reached
        shares = [value for value in shares_map.values() if value is not None]
        if (len(shares) < self.key):
            return (False, None)  # TODO: return error condition to indicate that there are too few shares to reconstruct key

        # attempt to recover key
        (secret_key, share_error) = algos.shamir_secret_sharing.reconstruct(shares)

        success = True
        # if there were providers that had invalid or missing shares
        if (len(shares) < len(self.roviders) or share_error):
            success = False

        return (success, secret_key)

    # distributes a new key to all providers
    # probably throws exception if the provider's put method fails
    def distribute_key(self, key):
        # compute new shares using len(providers) and k_key
        shares = algos.shamir_secret_sharing.share(key, self.k_key, len(self.providers))

        # write shares to providers
        for provider in self.providers:
            pass

    # creates a fresh master key
    def create_key(self):
        return "1234"
