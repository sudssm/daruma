# This is the main project

# TODO note to self: think about caching
# make a daemon to periodically garbage collect and ping / reload manifest

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
        # load the manifest here
        # ensures that we fail immediately with FatalOperationFailure if we recovered the wrong reconstruction threshold
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
        # make a copy of providers so that changes to the external list doesn't affect this one
        providers = providers[:]
        for provider in providers:
            # raises on failure
            provider.wipe()

        master_key = generate_key()
        manifest_name = generate_filename()
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

    def update_master_key(self):
        """
        Cycle the master key and rebootstrap
        """
        # diagnose with no errors. repairing the bootstrap will also cycle the master key
        self.resilience_manager.diagnose_and_repair_bootstrap([])

    def _reset(self):
        """
        Reprovision the system
        To be called after a core parameter change (change in provider or threshold)
        Raises FatalOperationFailure if there was an unrecoverable write error
        """
        self._load_manifest()
        try:
            self.file_manager.reset()
            self.update_master_key()
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            # don't try to repair - if we are here, all files got successfully refreshed
            self.resilience_manager.diagnose(e.failures)
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self._reset()
            raise

    def add_provider(self, provider):
        """
        Add the provider to the list of providers
        Increases the internal reconstruction thresholds by 1
        (Assumes that (n-k) should stay constant, which makes sense in the context of the working assumption
        that k=n-1)
        """
        providers = self.file_manager.providers
        providers.append(provider)

        file_reconstruction_threshold = self.file_manager.file_reconstruction_threshold + 1
        bootstrap_reconstruction_threshold = self.bootstrap_manager.bootstrap_reconstruction_threshold + 1

        self.change_params(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)

    def remove_provider(self, provider):
        """
        Remove the provider from the internal list of providers, if it exists
        Decreases the internal reconstruction thresholds by 1
        (Assumes that (n-k) should stay constant, which makes sense in the context of the working assumption
        that k=n-1)
        """
        providers = self.file_manager.providers
        if provider not in providers:
            return
        providers.remove(provider)

        file_reconstruction_threshold = self.file_manager.file_reconstruction_threshold - 1
        bootstrap_reconstruction_threshold = self.bootstrap_manager.bootstrap_reconstruction_threshold - 1

        self.change_params(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)

    def change_params(self, providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        Update the thresholds and providers for the system
        """
        self.file_manager.providers = providers
        self.bootstrap_manager.providers = providers
        self.resilience_manager.providers = providers

        self.bootstrap_manager.bootstrap_reconstruction_threshold = bootstrap_reconstruction_threshold
        self.file_manager.file_reconstruction_threshold = file_reconstruction_threshold
        self._reset()

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

    def ls(self, path):
        """
        Lists information about the entries at the given path.  If the given
        path points to a file, lists just the information about that file.

        Node information is represented by a dictionary with the following keys:
            - name
            - is_directory
            - size (only available if not is_directory)

        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        Raises InvalidPath or FatalOperationFailure if unsuccessful
        """
        self._load_manifest()
        return self.file_manager.ls(path)

    def mk_dir(self, path):
        """
        Create a directory
        Raises InvalidPath or FatalOperationFailure if unsuccessful
        """
        self._load_manifest()
        self.file_manager.mk_dir(path)

    def move(self, old_path, new_path):
        """
        Move a file or folder
        Raises InvalidPath if either path is invalid or if new_path exists
        """
        self._load_manifest()
        self.file_manager.move(old_path, new_path)

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
