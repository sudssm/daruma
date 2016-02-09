# This is the main project

# TODO note to self: think about caching

from managers.KeyManager import KeyManager
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename


class SecretBox:

    def __init__(self, providers, key_reconstruction_threshold, file_reconstruction_threshold):
        # key_reconstruction_threshold: the number of providers that need to be up to recover the key
        # file_reconstruction_threshold: the number of providers that need to be up to read files, given the key
        # providers: a list of providers

        if not self.verify_parameters(providers, key_reconstruction_threshold, file_reconstruction_threshold):
            raise exceptions.IllegalArgumentException

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
            try:
                provider.wipe()
            except exceptions.ProviderOperationFailure:
                # TODO maybe diagnose here?
                pass

        master_key = generate_key()
        manifest_name = generate_filename()

        try:
            self.key_manager.distribute_key_and_name(master_key, manifest_name)
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            # TODO if all are offline, raise network error?
            raise
        self.file_manager = FileManager(self.providers, self.file_reconstruction_threshold, master_key, manifest_name, setup=True)

    # alternative to provision, when we are resuming a previous session
    def start(self):
        try:
            master_key, manifest_name = self.key_manager.recover_key_and_name()
        except exceptions.OperationFailure as e:
            master_key, manifest_name = e.result
            # TODO diagnose and repair
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

        self.file_manager = FileManager(self.providers, self.file_reconstruction_threshold, master_key, manifest_name)

    # change the master key
    def update_master_key(self):
        master_key = generate_key()
        manifest_name = generate_filename()

        # upload new manifest first, then distribute new key to be atomic
        try:
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.key_manager.distribute_key_and_name(master_key, manifest_name)
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

    # public methods

    # add a new provider
    # TODO we get annoying edge cases if the user adds a provider, and then tries to add another before we update providers to reflect the first add
    def add_provider(self, provider):
        # TODO: use Doron's storage equation to determine if adding a new provider is worthwhile
            # will need to make calls to know the capacity of each provider
        """
        self.providers.append(provider)
        self.key_manager.distribute_new_key(master_key)
        # TODO: also need to update the file manager with the new master key
        # or make a new file manager
        self.file_manager.refresh()
        """

    def ls(self):
        # TODO maybe change this when we handle manifest caching?
        try:
            return self.file_manager.ls()
        except exceptions.OperationFailure as e:
            # TODO diagnose and repair
            return e.result
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

    def get(self, path):
        try:
            return self.file_manager.get(path)
        except exceptions.OperationFailure as e:
            # TODO diagnose and repair
            return e.result
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

    def put(self, path, data):
        try:
            return self.file_manager.put(path, data)
        except exceptions.OperationFailure as e:
            # TODO diagnose and repair
            return e.result
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

    def delete(self, path):
        try:
            return self.file_manager.delete(path)
        except exceptions.OperationFailure as e:
            # TODO diagnose and repair
            return e.result
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise
