# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from tools.utils import generate_random_name
# TODO cache the manifest intelligently


class FileManager:
    # set setup to True in order to create a new system
    def __init__(self, providers, file_reconstruction_threshold, master_key, manifest_name, setup=False):
        self.providers = providers
        self.file_reconstruction_threshold = file_reconstruction_threshold
        self.master_key = master_key
        self.manifest_name = manifest_name
        self.distributor = FileDistributor(providers, file_reconstruction_threshold)

        if setup:
            self.manifest = Manifest()
            self.distribute_manifest()
        # else:
        # self.load_manifest()

    def load_manifest(self):
        """
        Raises:
            OperationFailure with None result if any provider fails
            FatalOperationFailure if we couldn't load
        """
        self.manifest = None
        try:
            manifest_str = self.distributor.get(self.manifest_name, self.master_key)
            self.manifest = Manifest.deserialize(manifest_str)
        except exceptions.OperationFailure as e:
            # set manifest to recovered value and pass along failures
            self.manifest = Manifest.deserialize(e.result)
            raise exceptions.OperationFailure(e.failures, None)

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
        errors = []
        old_files = []
        new_distributor = FileDistributor(self.providers, self.file_reconstruction_threshold)

        for file_node in self.manifest.generate_files_under(""):
            filename = file_node.name
            old_codename = file_node.code_name
            old_key = file_node.key
            size = file_node.size

            try:
                data = self.distributor.get(old_codename, old_key)
            except exceptions.OperationFailure as e:
                data = e.data
                errors.append(e)
            old_files.append(old_codename)

            codename = generate_random_name()
            key = new_distributor.put(codename, data)
            # TODO this changes the manifest without being sure that distributor changes will work
            # change this when implementing manifest caching
            self.manifest.update_file(filename, codename, size, key)

        old_distributor = self.distributor
        self.distributor = new_distributor
        self.distribute_manifest()

        # TODO doing this step at the end means that we double in size
        # garbage collect
        for codename in old_files:
            try:
                old_distributor.delete(codename)
            except exceptions.OperationFailure as e:
                errors.append(e)

        if len(errors) > 0:
            raise exceptions.OperationFailure(errors)

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

    def put(self, name, data):
        """
        Raises FatalOperationFailure (from distributer.put) if any provider operation throws an exception
        """
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
        Raises InvalidPath (from manifest.create_directory) if the path is invalid for a directory
        Raises FatalOperationFailure (from distributor.put) if any provider operation throws an exception
        """
        self.manifest.create_directory(path)
        self.distribute_manifest()

    def move(self, old_path, new_path):
        """
        Move a file or folder from old_path to new_path
        Raises InvalidPath (from manifest.move) if either path is invalid, or if new_path exists
        """
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
        Raises FileNotFound if file does not exist (from manifest.remove_line)
        Raises OperationFailure with errors and file contents if recoverable (from distributor.delete)
            Raises FatalOperationFailure if unrecoverable (from distribute_manifest)
        """
        node = self.manifest.remove(name)

        try:
            self.distribute_manifest()
        except FatalOperationFailure:
            # local manifest is different from remote manifest; we need to rollback
            # TODO need a way to get the old manifest back
            # and then distribute it (handle when implementing caching)
            raise

        try:
            self.distributor.delete(node.code_name)
        except exceptions.FatalOperationFailure as e:
            # some provider deletes failed, but it wasn't fatal
            raise exceptions.OperationFailure(e.failures, None)
