# This is the main project

#TODO note to self: think about caching

from stubs import *
import algos


class SecretBox:

    def __init__(self, providers, k_key, k_file):
        # k_key: the number of providers that need to be up to recover the key
        # k_file: the number of providers that need to be up to read files, given the key
        # providers: a list of providers

        self.providers = providers
        self.k_key = k_key
        self.k_file = k_file

        # the key manager uses SSSS
        self.key_manager = KeyManager(self.providers, self.k_key)

        try:
            # TODO this method should redistribute the key if not all providers are configured
            self.master_key = self.key_manager.recover_key()

        except ProvidersUnconfigured:
            # case where no provider has a keyshare
            self.master_key = self.key_manager.create_master_key()
            self.key_manager.distribute_key(self.master_key)
            # TODO probably should catch connection errors
        except ProvidersDown:
            # case where some providers have keyshares, and others don't
            # and we have don't have enough shares to recover the key
            print "sorry, you're screwed (or maybe no internet connection?)"

        # at this point, all (reachable) providers are confirmed to have a valid keyshare
        # and we have recovered the master key

        # the file manager uses RS
        # TODO this method should, if a provider doesn't have a manifest, start syncing that provider in the background
        self.file_manager = FileManager(self.providers, self.k_file, self.master_key)

  # public methods

  # add a new provider
  # TODO we get annoying edge cases if the user adds a provider, and then tries to add another before we update providers to reflect the first add
    def add_provider(self, provider):
        self.providers.append(provider)
        self.key_manager.distribute_key(self.master_key)
        self.file_manager.refresh()

    def ls(self, path):
        return self.file_manager.ls(path)

    def get(self, path):
        return self.file_manager.get(path)

    def put(self, path, data):
        return self.file_manager.put(path, data)

    def delete(self, path):
        return self.file_manager.delete(path)
