# This is the main project

#TODO note to self: think about caching

from managers.KeyManager import KeyManager
from managers.FileManager import FileManager
from custom_exceptions import exceptions


class SecretBox:

    def __init__(self, providers, key_reconstruction_threshold, file_reconstruction_threshold):
        # key_reconstruction_threshold: the number of providers that need to be up to recover the key
        # file_reconstruction_threshold: the number of providers that need to be up to read files, given the key
        # providers: a list of providers

        if (not self.verify_parameters(providers, key_reconstruction_threshold, file_reconstruction_threshold)):
            raise exceptions.InvalidParametersException

        self.providers = providers
        self.key_reconstruction_threshold = key_reconstruction_threshold
        self.file_reconstruction_threshold = file_reconstruction_threshold

        # the key manager uses SSSS
        self.key_manager = KeyManager(self.providers, self.key_reconstruction_threshold)
        self.file_manager = None

    # TODO: update with other bad cases
    def verify_parameters(self, providers, key_reconstruction_threshold, file_reconstruction_threshold):
        return key_reconstruction_threshold >= 2 and \
            file_reconstruction_threshold >= 2 and \
            len(providers) >= 2 and \
            key_reconstruction_threshold < len(providers) and \
            file_reconstruction_threshold < len(providers)

    # start from scratch and create a new key
    def provision(self):
        for provider in self.providers:
            provider.wipe()

        self.master_key = self.key_manager.distribute_new_key()
        # TODO: error handling if we can't upload key shares
        self.file_manager = FileManager(self.providers, self.file_reconstruction_threshold, self.master_key)

        '''
        except ProvidersUnconfigured:
            # case where no provider has a keyshare
            self.master_key = self.key_manager.create_master_key()
            self.key_manager.distribute_new_key(self.master_key)
            # TODO probably should catch connection errors
        except ProvidersDown:
            # case where some providers have keyshares, and others don't
            # and we have don't have enough shares to recover the key
            print "sorry, you're screwed (or maybe no internet connection?)"
        '''

    # alternative to provision, when we are resuming a previous session
    def start(self):
        self.master_key = self.key_manager.recover_key()
        # TODO: error handling if we can't recover the key
        self.file_manager = FileManager(self.providers, self.file_reconstruction_threshold, self.master_key)

  # public methods

  # add a new provider
  # TODO we get annoying edge cases if the user adds a provider, and then tries to add another before we update providers to reflect the first add
    def add_provider(self, provider):
        # TODO: use Doron's storage equation to determine if adding a new provider is worthwhile
            # will need to make calls to know the capacity of each provider
        '''
        self.providers.append(provider)
        self.key_manager.distribute_new_key(self.master_key)
        # TODO: also need to update the file manager with the new master key
        # or make a new file manager
        self.file_manager.refresh()
        '''

    def ls(self):
        return self.file_manager.ls()

    def get(self, path):
        return self.file_manager.get(path)

    def put(self, path, data):
        return self.file_manager.put(path, data)

    def delete(self, path):
        return self.file_manager.delete(path)
