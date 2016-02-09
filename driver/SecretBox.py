# This is the main project

# TODO note to self: think about caching

from managers.BootstrapManager import BootstrapManager, Bootstrap
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename


class SecretBox:

    # construct a new secretbox
    # in normal usage, one should use the static load or provision methods
    def __init__(self, bootstrap_manager, file_manager):
        self.bootstrap_manager = bootstrap_manager
        self.file_manager = file_manager

    # start from scratch
    @staticmethod
    def provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        # providers: a list of providers
        # bootstrap_reconstruction_threshold: the number of providers that need to be up to recover the key
        # file_reconstruction_threshold: the number of providers that need to be up to read files, given the key

        for provider in providers:
            try:
                provider.wipe()
            except exceptions.ProviderOperationFailure:
                # TODO maybe diagnose here?
                # or maybe crash -- can't provision if one provider is down already
                pass

        master_key = generate_key()
        manifest_name = generate_filename()
        bootstrap = Bootstrap(master_key, manifest_name, file_reconstruction_threshold)

        # the bootstrap manager uses SSSS
        bootstrap_manager = BootstrapManager(providers, bootstrap_reconstruction_threshold)

        try:
            bootstrap_manager.distribute_bootstrap(bootstrap)
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

        file_manager = FileManager(providers, file_reconstruction_threshold, master_key, manifest_name, setup=True)
        return SecretBox(bootstrap_manager, file_manager)

    # alternative to provision, when we are resuming a previous session
    @staticmethod
    def load(providers):
        bootstrap_manager = BootstrapManager(providers)
        try:
            bootstrap = bootstrap_manager.recover_bootstrap()
        except exceptions.OperationFailure as e:
            bootstrap = e.result
            # TODO diagnose and repair
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

        file_manager = FileManager(providers, bootstrap.file_reconstruction_threshold, bootstrap.key, bootstrap.manifest_name)
        return SecretBox(bootstrap_manager, file_manager)

    # TODO: update with other bad cases
    def _verify_parameters(self, providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        return bootstrap_reconstruction_threshold >= 2 and \
            file_reconstruction_threshold >= 2 and \
            len(providers) >= 2 and \
            bootstrap_reconstruction_threshold < len(providers) and \
            file_reconstruction_threshold < len(providers)

    # change the master key
    def update_master_key(self):
        master_key = generate_key()
        manifest_name = generate_filename()

        # upload new manifest first, then distribute new key to be atomic
        try:
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.bootstrap_manager.distribute_bootstrap(master_key, manifest_name)
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
        self.bootstrap_manager.distribute_new_key(master_key)
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
