# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from tools.utils import generate_random_name, run_parallel
# TODO cache the manifest intelligently


class FileManager:
    """
    A distributed filesystem. Wraps Distributor and Manifest to encrypt and distribute files across multiple providers.
    Detects errors in providers, and raises them as OperationFailure or FatalOperationFailure. Also detects missing providers.
    Does not attempt to do any recovery or repair of broken providers.
    """
    def __init__(self, providers, num_providers, file_reconstruction_threshold, master_key, manifest_name, setup=False):
        """
        Create a FileManager
        Args:
            providers: a list of providers to use
            num_providers: the total number of providers that have been configured with this system before
            file_reconstruction_threshold: the threshold for file file_reconstruction_threshold
            master_key: the master key used to decrypt files
            manifest_name: the name of the manifest file on the providers
            setup: whether this FileManager should setup a new system (True) or load an existing one (False)
        """
        self.providers = providers
        self.file_reconstruction_threshold = file_reconstruction_threshold
        self.master_key = master_key
        self.manifest_name = manifest_name
        self.distributor = FileDistributor(providers, num_providers, file_reconstruction_threshold)

        if setup:
            self.manifest = Manifest(self.providers)
            self.distribute_manifest()
            self.missing_providers = []
        # else:
        # self.load_manifest()

    def load_manifest(self, discard_extra_providers=False):
        """
        Loads the manifest into memory
        Also compiles a list of missing providers for later use
        Args: If discard_extra_providers is True, will internally discard any providers not in the manifest
        Raises:
            OperationFailure with None result if any provider fails
            FatalOperationFailure if we couldn't load
        """
        self.manifest = None
        failures = None
        try:
            manifest_str = self.distributor.get(self.manifest_name, self.master_key)
        except exceptions.OperationFailure as e:
            manifest_str = e.result
            failures = e.failures

        self.manifest = Manifest.deserialize(manifest_str)
        providers_uuids = set(map(lambda provider: provider.uuid, self.providers))
        expected_providers = set(self.manifest.get_provider_strings())
        self.missing_providers = list(expected_providers - providers_uuids)

        if discard_extra_providers:
            # remove any extra providers
            self.providers = filter(lambda provider: provider.uuid in expected_providers, self.providers)
            self.distributor.providers = self.providers

        if failures is not None:
            raise exceptions.OperationFailure(failures, None)

    def get_missing_providers(self):
        """
        Returns a list of unique identifier tuples for providers that are expected but missing
        If the resulting list is nonempty, the system is in readonly mode
        """
        return self.missing_providers[:]

    def add_missing_provider(self, missing_provider):
        """
        Add a missing provider to this file manager
        Args:
            missing_provider: a missing provider, with a uuid in the result of calling missing_providers()
        Returns:
            True if the provided missing_provider is one of the missing_providers
            False otherwise
        """
        try:
            self.missing_providers.remove(missing_provider.uuid)
        except ValueError:
            # the provided missing_provider was not in the list of missing_providers
            return False

        self.providers.append(missing_provider)
        self.distributor.providers.append(missing_provider)

        return True

    def distribute_manifest(self):
        """
        Raises FatalOperationFailure if any provider fails
        """
        content = self.manifest.serialize()
        self.distributor.put(self.manifest_name, content, self.master_key)

    def update_key_and_name(self, master_key, manifest_name):
        self.master_key = master_key
        self.manifest_name = manifest_name
        self.distribute_manifest()
        # TODO make sure this doesnt go to infinite loop on repeated distributes

    def reset(self):
        """
        Refresh all files on the filesystem by re-encrypting, sharing, and distributing all files and manifest
        To be called after changing either providers or file_reconstruction_threshold
        Constructs a new FileDistributor object with the new parameters
        NB: during the operation, the amount of space used on each provider doubles
        """
        old_files = []

        # we use num_providers = len(providers) here, because we want to reprovision with all current providers
        new_distributor = FileDistributor(self.providers, len(self.providers), self.file_reconstruction_threshold)

        def duplicate_file(file_node):
            filename = file_node.name
            old_codename = file_node.code_name
            old_key = file_node.key
            size = file_node.size

            data = self.distributor.get(old_codename, old_key)
            old_files.append(old_codename)

            codename = generate_random_name()
            key = new_distributor.put(codename, data)
            # TODO this changes the manifest without being sure that distributor changes will work
            # change this when implementing manifest caching
            self.manifest.update_file(filename, codename, size, key)

        dup_failures = run_parallel(duplicate_file, map(lambda (path, node): [node], self.manifest.generate_nodes_under("")))
        failures = []
        for failure in dup_failures:
            try:
                failures = failures + failure.failures
            except AttributeError:
                failures.append(failure)

        if len(failures) > 0:
            raise exceptions.FatalOperationFailure(failures)

        old_distributor = self.distributor
        self.distributor = new_distributor

        self.manifest.set_providers(self.providers)
        self.distribute_manifest()

        # TODO doing this step at the end means that we double in size
        # garbage collect
        def delete_codename(codename):
            old_distributor.delete(codename)

        failures = run_parallel(delete_codename, map(lambda codename: [codename], old_files))
        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, None)

    def path_generator(self):
        """
        Yields the paths for all files and directories in the system.
        """
        for node_path, _ in self.manifest.generate_nodes_under(""):
            yield node_path

    def ls(self, path):
        """
        Lists information about the entries at the given path.  If the given
        path points to a file, lists just the information about that file.

        Node information is represented by a dictionary with the following keys:
            - name
            - is_directory
            - size (only available if not is_directory)

        Args:
            path: A string corresponding to the path of the directory to list.
                  (the empty string will query the root directory)

        Returns: A list of dictionaries corresponding to the names of files and
                 and directories in the specified directory.

        Raises:
            InvalidPath (from manifest.list_directory_entries) if the path does
            not exist.
        """
        def external_attributes_from_node(node):
            external_attributes = {
                "name": node.name,
                "is_directory": False,
            }

            try:
                external_attributes["size"] = node.size
            except AttributeError:
                # The node is a directory
                external_attributes["is_directory"] = True

            return external_attributes
        target_node = self.manifest.get(path)
        try:
            ls_nodes = target_node.get_children()
        except AttributeError:
            # We assumed target_node was a Directory, but it's actually a file.
            ls_nodes = [target_node]

        return [external_attributes_from_node(node) for node in ls_nodes]

    def _check_read_only(self):
        """
        Check to see if the system is in read only mode by checking self.missing_providers
        To be called after loading manifest
        Raises ReadOnlyMode if in ready only mode
        """
        if len(self.missing_providers) > 0:
            raise exceptions.ReadOnlyMode

    def put(self, name, data):
        """
        Raises ReadOnlyMode if the system is in read only mode (there are some missing providers)
        Raises FatalOperationFailure (from distributer.put) if any provider operation throws an exception
        """
        self._check_read_only()

        codename = generate_random_name()
        key = self.distributor.put(codename, data)

        old_node = self.manifest.update_file(name, codename, len(data), key)

        # update the manifest
        self.distribute_manifest()

        # we are performing a replacement
        if old_node is not None:
            try:
                self.distributor.delete(old_node.code_name)
            except exceptions.FatalOperationFailure as e:
                # this isn't actually fatal - we just have some extra garbage floating around
                raise exceptions.OperationFailure(e.failures, None)

    def mk_dir(self, path):
        """
        Creates a directory with the specified path, creating intermediate directories along the way
        Does nothing if the directory already exists
        Raises ReadOnlyMode if the system is in read only mode (there are some missing providers)
        Raises InvalidPath (from manifest.create_directory) if the path is invalid for a directory
        Raises FatalOperationFailure (from distributor.put) if any provider operation throws an exception
        """
        self._check_read_only()

        self.manifest.create_directory(path)
        self.distribute_manifest()

    def move(self, old_path, new_path):
        """
        Move a file or folder from old_path to new_path
        Raises ReadOnlyMode if the system is in read only mode (there are some missing providers)
        Raises InvalidPath (from manifest.move) if either path is invalid, or if new_path exists
        """
        self._check_read_only()

        self.manifest.move(old_path, new_path)
        self.distribute_manifest()

    def get(self, name):
        """
        attempt to get a file
        Returns file contents
        Raises FileNotFound if file does not exist
        Raises OperationFailure with errors and file contents if recoverable (from distributor.get)
        Raises FatalOperationFailure if unrecoverable (from distributor.get)
        """
        try:
            node = self.manifest.get(name)
        except exceptions.InvalidPath:
            raise exceptions.FileNotFound

        codename = node.code_name
        key = node.key

        return self.distributor.get(codename, key)

    def delete(self, name):
        """
        delete a file
        Raises ReadOnlyMode if the system is in read only mode (there are some missing providers)
        Raises FileNotFound if file does not exist (from manifest.remove_line)
        Raises OperationFailure with errors and file contents if recoverable (from distributor.delete)
        Raises FatalOperationFailure if unrecoverable (from distribute_manifest)
        """
        self._check_read_only()

        node = self.manifest.remove(name)

        try:
            self.distribute_manifest()
        except exceptions.FatalOperationFailure:
            # local manifest is different from remote manifest; we need to rollback
            # TODO need a way to get the old manifest back
            # and then distribute it (handle when implementing caching)
            raise

        try:
            self.distributor.delete(node.code_name)
        except AttributeError:
            # We assumed node was a file, but it's actually a directory.
            pass
        except exceptions.FatalOperationFailure as e:
            # some provider deletes failed, but it wasn't fatal
            raise exceptions.OperationFailure(e.failures, None)
