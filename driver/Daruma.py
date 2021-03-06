# This is the main project

# TODO note to self: think about caching
# make a daemon to periodically garbage collect and ping / reload manifest

import logging
import threading
from managers.ResilienceManager import ResilienceManager
from managers.BootstrapManager import BootstrapManager, Bootstrap
from managers.FileManager import FileManager
from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_random_name, run_parallel

logger = logging.getLogger("daruma")


class Daruma:

    def __init__(self, bootstrap_manager, file_manager, resilience_manager, load_manifest=True):
        """
        Construct a new Daruma object
        NB: In normal usage, one should use the static load or provision methods
        """
        self.lock = threading.RLock()
        self.bootstrap_manager = bootstrap_manager
        self.file_manager = file_manager
        self.resilience_manager = resilience_manager

        if load_manifest:
            # ensures that we fail immediately with FatalOperationFailure if we recovered the wrong reconstruction threshold
            self._load_manifest(discard_extra_providers=True)

    def synchronized(method):
        def synchronized_method(self, *args, **kwargs):
            with self.lock:
                return method(self, *args, **kwargs)
        return synchronized_method

    @staticmethod
    def _assert_valid_params(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        makes sure the reconstruction thresholds are within a suitable range (1 through len(providers)-1, inclusive) and that we have at least 3 providers
        """
        if bootstrap_reconstruction_threshold < 2 or bootstrap_reconstruction_threshold >= len(providers) or \
           file_reconstruction_threshold < 2 or file_reconstruction_threshold >= len(providers) or \
           len(providers) < 3:
            raise ValueError("Invalid parameters!")

    @staticmethod
    def provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        Create a new Daruma.
        Warning: Deletes all files on all providers! Even if a FatalOperationFailure is thrown, files on all providers will be unstable or deleted.
        Args:
            providers: a list of providers
            bootstrap_reconstruction_threshold: the number of providers that need to be up to recover the key. Between 1 and len(providers)-1, inclusive
            file_reconstruction_threshold: the number of providers that need to be up to read files, given the key. Between 1 and len(providers)-1, inclusive
        Returns a constructed Daruma object
        Raises:
            ValueError if arguments are invalid
            FatalOperationFailure if provisioning failed
        """
        logger.debug("provisioning: brt=%d, frt=%d", bootstrap_reconstruction_threshold, file_reconstruction_threshold)
        Daruma._assert_valid_params(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)
        # make a copy of providers so that changes to the external list doesn't affect this one
        providers = providers[:]

        def wipe(provider):
            provider.wipe()
        failures = run_parallel(wipe, map(lambda provider: [provider], providers))
        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)

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

        file_manager = FileManager(providers, len(providers), file_reconstruction_threshold, master_key, manifest_name, setup=True)
        resilience_manager = ResilienceManager(providers, file_manager, bootstrap_manager)
        return Daruma(bootstrap_manager, file_manager, resilience_manager, load_manifest=False)

    @staticmethod
    def load(providers):
        """
        Load an existing Daruma
        Args: providers, a list of providers
        Returns (Daruma, extra_providers)
            Daruma: a constructed Daruma object
            extra_providers: a list of providers that were provided but not part of the loaded installation
        The client should decide whether to discard the extra_providers or to reprovision with them
        Raises FatalOperationFailure
        """
        logger.debug("loading")
        providers = providers[:]
        bootstrap_manager = BootstrapManager(providers)
        failures = []
        try:
            bootstrap, num_providers = bootstrap_manager.recover_bootstrap()
        except exceptions.OperationFailure as e:
            bootstrap, num_providers = e.result
            failures += e.failures
        except exceptions.FatalOperationFailure:
            # TODO check for network error
            raise

        file_manager = FileManager(providers, num_providers, bootstrap.file_reconstruction_threshold, bootstrap.key, bootstrap.manifest_name)
        # TODO this may load some cached state from disk
        resilience_manager = ResilienceManager(providers, file_manager, bootstrap_manager)

        if len(failures) > 0:
            resilience_manager.diagnose_and_repair_bootstrap(failures)

        daruma = Daruma(bootstrap_manager, file_manager, resilience_manager)
        extra_providers = list(set(providers) - set(daruma.file_manager.providers))
        return daruma, extra_providers

    @synchronized
    def update_master_key(self):
        """
        Cycle the master key and rebootstrap
        This method is thread-safe.
        """
        logger.debug("updating master key")
        # diagnose with no errors. repairing the bootstrap will also cycle the master key
        self.resilience_manager.diagnose_and_repair_bootstrap([])

    @synchronized
    def add_missing_provider(self, missing_provider):
        """
        Add a missing provider to the system. Used to get out of read only mode
        Does nothing if the provider is not one of the missing providers.
        This method is thread-safe.
        Args:
            missing_provider: a provider object that is one of the provider uuids returned by get_missing_providers
        Returns:
            True if the supplied missing_provider is one of the the missing providers, False otherwise
        """
        logger.debug("adding a missing provider")
        if not self.file_manager.add_missing_provider(missing_provider):
            return False
        # this was a correct missing provider; we can use it
        self._set_all_internal_providers(self.file_manager.providers)

        return True

    def _set_all_internal_providers(self, providers):
        """
        Sets the internal provider objects for all submanagers
        """
        self.file_manager.providers = providers
        self.bootstrap_manager.providers = providers
        self.resilience_manager.providers = providers

    def _reset(self):
        """
        Reprovision the system
        To be called after a core parameter change (change in provider or threshold)
        Raises FatalOperationFailure if there was an unrecoverable write error
        """
        logger.debug("_resetting")
        try:
            self.file_manager.reset()
            self.update_master_key()
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            # this should never occur
            logger.error("Unexpected Operation Failure in _reset")
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self._reset()
            raise

    @synchronized
    def reprovision(self, providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold):
        """
        Update the thresholds and providers for the system
        Will redistribute every file across the new provider list
        This method is thread-safe.
        Args:
            providers: a list of provider objects across which to distribute
            bootstrap_reconstruction_threshold: the new bootstrap threshold. Between 1 and len(providers)-1, inclusive
            file_reconstruction_threshold: the new file threshold. Between 1 and len(providers)-1, inclusive
        Raises:
            ValueError if arguments are invalid
        """
        logger.debug("reprovisioning: brt=%d, frt=%d", bootstrap_reconstruction_threshold, file_reconstruction_threshold)
        Daruma._assert_valid_params(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)
        # do nothing if params are the same
        if providers == self.file_manager.providers and \
           bootstrap_reconstruction_threshold == self.bootstrap_manager.bootstrap_reconstruction_threshold and \
           file_reconstruction_threshold == self.file_manager.file_reconstruction_threshold:
                return

        old_providers = self.file_manager.providers

        self._set_all_internal_providers(providers)

        self.bootstrap_manager.bootstrap_reconstruction_threshold = bootstrap_reconstruction_threshold
        self.file_manager.file_reconstruction_threshold = file_reconstruction_threshold

        self._reset()

        # wipe the providers that were used previously but aren't any longer
        def remove(provider):
            provider.remove()
        run_parallel(remove, map(lambda provider: [provider], set(old_providers) - set(providers)))

    def _load_manifest(self, discard_extra_providers=False):
        """
        Load the manifest into the file manager
        Without caching, this should be called before every public operation
        Args: If discard_extra_providers is True, will discard any providers not in the manifest
        Raises FatalOperationFailure if the load was not successful
        """
        logger.debug("loading manifest")
        # TODO handle manifest caching
        try:
            self.file_manager.load_manifest(discard_extra_providers)
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose_and_repair_bootstrap(e.failures)
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self._load_manifest(discard_extra_providers)
            raise

        if discard_extra_providers:
            self._set_all_internal_providers(self.file_manager.providers)

    @synchronized
    def get_missing_providers(self):
        """
        Gets a list of the providers needed to be added before the system can be writable
        Is empty if and only if the system is not in read only mode
        To get out of read only mode, either call add_missing_providers or reprovision
        This method is thread-safe.
        """
        logger.debug("getting missing providers")
        return self.file_manager.get_missing_providers()

    @synchronized
    def get_providers(self):
        """
        This method is thread-safe.
        """
        logger.debug("getting providers")
        return self.file_manager.providers[:]

    @synchronized
    def ls(self, path):
        """
        Lists information about the entries at the given path.  If the given
        path points to a file, lists just the information about that file.

        Node information is represented by a dictionary with the following keys:
            - name
            - is_directory
            - size (only available if not is_directory)

        Note that this method reads a cached version of the system manifest and
        does not re-download it for verification.
        This method is thread-safe.
        Raises InvalidPath.
        """
        logger.debug("ls-ing %s", path)
        return self.file_manager.ls(path)

    @synchronized
    def mk_dir(self, path):
        """
        Create a directory
        This method is thread-safe.
        Raises InvalidPath or FatalOperationFailure if unsuccessful
        Raises ReadOnlyMode if the system is in ReadOnlyMode
        """
        logger.debug("making a directory: %s", path)
        self._load_manifest()
        self.file_manager.mk_dir(path)

    @synchronized
    def move(self, old_path, new_path):
        """
        Move a file or folder
        This method is thread-safe.
        Raises InvalidPath if either path is invalid or if new_path exists
        Raises ReadOnlyMode if the system is in ReadOnlyMode
        Raises FatalOperationFailure if unsuccessful
        """
        logger.debug("moving %s to %s", old_path, new_path)
        self._load_manifest()
        self.file_manager.move(old_path, new_path)

    @synchronized
    def get(self, path):
        """
        Get the contents of a file given the file path
        If some providers are in error, attempts to repair them
        Note that this method reads a cached version of the system manifest and
        does not re-download it for verification.
        Upon return either all providers are stable or at least one provider is RED.
        This method is thread-safe.
        Raises FileNotFound if path is invalid
        Raises FatalOperationFailure if unsuccessful
        """
        logger.debug("getting %s", path)
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

    @synchronized
    def put(self, path, data):
        """
        Put the data to path location
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        This method is thread-safe.
        Raises FatalOperationFailure if unsuccessful
        Raises ReadOnlyMode if the system is in ReadOnlyMode
        """
        logger.debug("putting into %s", path)
        self._load_manifest()

        try:
            result = self.file_manager.put(path, data)
            self.resilience_manager.log_success()
            return result
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose(e.failures)
            self.resilience_manager.garbage_collect()
            return e.result
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self.put(path, data)
            raise

    @synchronized
    def delete(self, path):
        """
        Delete the data at path
        If some providers are in error, attempts to repair them
        Upon return either all providers are stable or at least one provider is RED
        This method is thread-safe.
        Raises FileNotFound if path is invalid
        Raises FatalOperationFailure if unsuccessful
        Raises ReadOnlyMode if the system is in ReadOnlyMode
        """
        logger.debug("deleting %s", path)
        self._load_manifest()

        try:
            self.file_manager.delete(path)
            self.resilience_manager.log_success()
        except exceptions.OperationFailure as e:
            self.resilience_manager.diagnose(e.failures)
            self.resilience_manager.garbage_collect()
            return e.result
        except exceptions.FatalOperationFailure as e:
            can_retry = self.resilience_manager.diagnose(e.failures)
            if can_retry:
                return self.delete(path)
            raise

    @synchronized
    def list_all_paths(self):
        """
        Returns a generator for the paths to all files and directories in the system.
        Note that this method reads a cached version of the system manifest and
        does not re-download it for verification.
        This method is thread-safe.
        """
        logger.debug("listing all paths")
        return self.file_manager.path_generator()
