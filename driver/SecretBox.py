# This is the main project

# TODO note to self: think about caching
# make a daemon to periodically garbage collect and ping / reload manifest

from managers.ResilienceManager import ResilienceManager
from managers.BootstrapManager import BootstrapManager, Bootstrap
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_random_name


class SecretBox:

    def __init__(self, bootstrap_manager, file_manager, resilience_manager):
        """
        Construct a new SecretBox object
        NB: In normal usage, one should use the static load or provision methods
        """
        self.bootstrap_manager = bootstrap_manager
        self.file_manager = file_manager
        self.resilience_manager = resilience_manager
        # load the manifest here
        # ensures that we fail immediately with FatalOperationError if we recovered the wrong reconstruction threshold
        self._load_manifest()

    @staticmethod
    def provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        Create a new SecretBox
        Providers: a list of providers
        bootstrap_reconstruction_threshold: the number of providers that need to be up to recover the key
        file_reconstruction_threshold: the number of providers that need to be up to read files, given the key
        Returns a constructed SecretBox object
        Raises FatalOperationFailure or ProviderFailure
        """

        for provider in providers:
            # raises on failure
            provider.wipe()

        master_key = generate_key()
        manifest_name = generate_random_name()
        bootstrap = Bootstrap(master_key, manifest_name, file_reconstruction_threshold)

        # the bootstrap manager uses SSSS
        bootstrap_manager = BootstrapManager(providers, bootstrap_reconstruction_threshold)

        try:
            bootstrap_manager.distribute_bootstrap(bootstrap)
        except exceptions.FatalOperationFailure:
            # TODO check for network error
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
        Raises FatalOperationFailure
        """
        bootstrap_manager = BootstrapManager(providers)
        failures = []
        try:
            bootstrap = bootstrap_manager.recover_bootstrap()
        except exceptions.OperationFailure as e:
            bootstrap = e.result
            failures += e.failures
        except exceptions.FatalOperationFailure:
            # TODO check for network error
            raise

        file_manager = FileManager(providers, bootstrap.file_reconstruction_threshold, bootstrap.key, bootstrap.manifest_name)
        # TODO this may load some cached state from disk
        resilience_manager = ResilienceManager(providers, file_manager, bootstrap_manager)

        if len(failures) > 0:
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
    def update_master_key(self):
        # diagnose with no errors. repairing the bootstrap will also cycle the master key
        self.resilience_manager.diagnose_and_repair_bootstrap([])
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
        """
        Load the manifest into the file manager
        Without caching, this should be called before every public operation
        Raises FatalOperationFailure if the load was not successful
        """
        # TODO handle manifest caching
        try:
            self.file_manager.load_manifest()
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose_and_repair_bootstrap(e.failures)
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self._load_manifest()
            raise

    def ls(self):
        """
        List the files in the system
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        Raises FatalOperationFailure if unsuccessful
        """
        self._load_manifest()
        return self.file_manager.ls()

    def get(self, path):
        """
        Get the contents of a file given the file path
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        Raises FileNotFound if path is invalid
        Raises FatalOperationFailure if unsuccessful
        """
        self._load_manifest()

        try:
            result = self.file_manager.get(path)
            self.resilience_manager.log_success()
            return result
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose_and_repair_file(e.failures, path, e.result)
            return e.result
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self.get(path)
            raise

    def put(self, path, data):
        """
        Put the data to path location
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        Raises FatalOperationFailure if unsuccessful
        """
        self._load_manifest()

        try:
            result = self.file_manager.put(path, data)
            self.resilience_manager.log_success()
            return result
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self.put(path, data)
            raise

    def delete(self, path):
        """
        Delete the data at path
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        Raises FileNotFound if path is invalid
        Raises FatalOperationFailure if unsuccessful
        """
        self._load_manifest()

        try:
            self.file_manager.delete(path)
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose(e.failures)
            self.resilience_manager.garbage_collect()
            return e.result
        except exceptions.FatalOperationFailure:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self.delete(path)
            raise
