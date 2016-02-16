# This is the main project

# TODO note to self: think about caching

from managers.ResilienceManager import ResilienceManager
from managers.BootstrapManager import BootstrapManager, Bootstrap
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename


class SecretBox:

    def __init__(self, bootstrap_manager, file_manager, resilience_manager):
        """
        Construct a new SecretBox object
        NB: In normal usage, one should use the static load or provision methods
        """
        self.bootstrap_manager = bootstrap_manager
        self.file_manager = file_manager
        self.resilience_manager = resilience_manager

    @staticmethod
    def provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        Create a new SecretBox
        Providers: a list of providers
        bootstrap_reconstruction_threshold: the number of providers that need to be up to recover the key
        file_reconstruction_threshold: the number of providers that need to be up to read files, given the key
        Returns a constructed SecretBox object
        Raises FatalOperationFailure or OperationFailure
        """

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
            # TODO if all are offline, raise network error?
            raise

        file_manager = FileManager(providers, file_reconstruction_threshold, master_key, manifest_name, setup=True)
        resilience_manager = ResilienceManager(providers, file_manager, bootstrap_manager)
        return SecretBox(bootstrap_manager, file_manager, resilience_manager)

    @staticmethod
    def load(providers):
        """
        Load an existing SecretBox
        Providers: a list of providers
        Returns a constructed SecretBox object
        Raises FatalOperationFailure or OperationFailure
        """
        bootstrap_manager = BootstrapManager(providers)
        failures = []
        try:
            bootstrap = bootstrap_manager.recover_bootstrap()
        except exceptions.OperationFailure as e:
            bootstrap = e.result
            failures += e.failures
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise

        file_manager = FileManager(providers, bootstrap.file_reconstruction_threshold, bootstrap.key, bootstrap.manifest_name)
        # TODO this may load some cached state from disk
        resilience_manager = ResilienceManager(providers, file_manager, bootstrap_manager)

        if failures is not None:
            resilience_manager.diagnose_and_repair_bootstrap(failures)

        return SecretBox(bootstrap_manager, file_manager, resilience_manager)

    # TODO: update with other bad cases
    def _verify_parameters(self, providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        return bootstrap_reconstruction_threshold >= 2 and \
            file_reconstruction_threshold >= 2 and \
            len(providers) >= 2 and \
            bootstrap_reconstruction_threshold < len(providers) and \
            file_reconstruction_threshold < len(providers)

    # change the master key
    # TODO this is the same as diagnose_and_repair_bootstrap
    def update_master_key(self):
        master_key = generate_key()
        manifest_name = generate_filename()

        bootstrap = Bootstrap(master_key, manifest_name, self.file_manager.file_reconstruction_threshold)

        # upload new manifest first, then distribute new key to be atomic
        try:
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.bootstrap_manager.distribute_bootstrap(bootstrap)
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

    def _load_manifest(self):
        # TODO handle manifest caching
        try:
            self.file_manager.load_manifest()
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose_and_repair_bootstrap(e.failures)
        except exceptions.FatalOperationFailure as e:
            # TODO diagnose
            raise

    def ls(self):
        self._load_manifest()

        return self.file_manager.ls()

    def get(self, path):
        self._load_manifest()

        try:
            return self.file_manager.get(path)
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose_and_repair_file(e.failures, path, e.result)
            return e.result
        except exceptions.FatalOperationFailure:
            self.reslience_manager.diagnose(failures)
            raise

    def put(self, path, data):
        self._load_manifest()

        try:
            return self.file_manager.put(path, data)
        except exceptions.FatalOperationFailure:
            self.reslience_manager.diagnose(failures)
            raise

    def delete(self, path):
        self._load_manifest()

        try:
            return self.file_manager.delete(path)
        except exceptions.OperationFailure as e:
            # TODO diagnose and repair
            # repair here is just garbage collect
            return e.result
        except exceptions.FatalOperationFailure:
            # TODO diagnose
            raise
