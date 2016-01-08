from custom_exceptions import exceptions
from crypto import encryption, erasure_encoding

# For RS distributing files
# TODO make resistant to provider going down and other error cases


class FileDistributor:
    def __init__(self, providers, file_reconstruction_threshold):
        self.providers = providers
        self.num_providers = len(providers)
        self.file_reconstruction_threshold = file_reconstruction_threshold

    # returns the key that this file was shared with
    # key is an optional key to use to encrypt
    # in practice, key should only be defined for the manifest, since we must use the master key
    def put(self, filename, data, key=None):
        # encrypt
        if key is None:
            key = encryption.generate_key()
        ciphertext = encryption.encrypt(data, key)

        # compute RS
        shares = erasure_encoding.share(ciphertext, self.file_reconstruction_threshold, self.num_providers)

        # TODO, parallel?
        # callback function?
        # consider early return when k are done, and finish in background?
        # upload to each provider
        for provider, share in zip(self.providers, shares):
            provider.put(filename, share)

        # TODO: error handling if some providers indicate upload failure

        return key

    def get(self, filename, key):
        def get_share(provider):
            try:
                return provider.get(filename)
            except exceptions.ProviderFileNotFound:
                return None
            # TODO except other things?

        # download shares
        shares = [get_share(provider) for provider in self.providers]
        shares = [share for share in shares if share is not None]
        if len(shares) == 0:
            # no shares found - assume file doesn't exist
            raise exceptions.FileNotFound

        # TODO: address the case where some providers don't return shares?

        # un RS
        ciphertext = erasure_encoding.reconstruct(shares, self.file_reconstruction_threshold, self.num_providers)
        # decrypt
        data = encryption.decrypt(ciphertext, key)  # TODO: deal with failed auth

        return data

    def delete(self, filename):
        for provider in self.providers:
            try:
                provider.delete(filename)
            except exceptions.ProviderFileNotFound:
                pass
