from custom_exceptions import exceptions
import bson
import os.path


class Attributes():
    NAME = "name"
    CODE_NAME = "code_name"
    SIZE = "size"
    KEY = "key"
    CHILDREN = "children"


class _Node(object):
    """
    Superclass for elements in our file system tree.
    All node state is stored in an attributes dictionary that is
    BSON-serializable.  Notably, this means that references to other nodes (e.g.
    children of directories) are stored as references to their attributes, as
    _Node objects (and their subclasses) will be constructed on the fly to wrap
    them as needed.  This allows for very simple serialization and
    deserialization.
    """
    def __init__(self, attributes):
        """
        Creates a node around an existing set of attributes.  Should not be
        called directly, instead call _node_from_attributes() or a subclass's
        from_values() method.
        N.B. attributes must minimally include a name entry.
        """
        self.attributes = attributes

    def __cmp__(self, other):
        """
        _Nodes are comparable by the values in their backing dictionaries.
        """
        return cmp(self.attributes, other.attributes)

    @property
    def name(self):
        return self.attributes[Attributes.NAME]


class File(_Node):
    """
    The leaves in our tree structure.
    Contains information about individual files.
    """
    @staticmethod
    def from_values(name, code_name, size, key):
        """
        Args:
            name: string of true file name (not the path).
            code_name: string of code name.
            size: decimal value of file size.
            key: byte representation of encryption key.

        Returns:
            A File object initialized with the given arguments.
        """
        attributes = {
            Attributes.NAME: name,
            Attributes.CODE_NAME: code_name,
            Attributes.SIZE: size,
            Attributes.KEY: key
        }
        return File(attributes)

    @property
    def code_name(self):
        return self.attributes[Attributes.CODE_NAME]

    @property
    def key(self):
        return self.attributes[Attributes.KEY]

    @property
    def size(self):
        return self.attributes[Attributes.SIZE]


class Directory(_Node):
    """
    The internal nodes in our tree structure.
    Contains information on child Files and Directories.
    """
    @staticmethod
    def from_values(name, children=None):
        """
        Args:
            name: string of Directory name (not the path).
            children: list of uniquely named File and Directory objects.

        Returns:
            A Directory object initialized with the given arguments.
        """
        if children is None:
            children_dict = {}
        else:
            children_dict = {child.name: child.attributes for child in children}

        attributes = {
                        Attributes.NAME: name,
                        Attributes.CHILDREN: children_dict
                     }
        return Directory(attributes)

    def get_children(self):
        """
        A list of the immediate children Files and Directories of this
        directory.
        """
        children = self.attributes[Attributes.CHILDREN]
        return [_node_from_attributes(child) for child in children.values()]

    def _add_child(self, child_node):
        """
        Adds a child to the directory, overwriting any existing children with
        the same name.

        Args:
            child_node: A File or Directory object to be added.

        Returns:
            The child node with the same name that was replaced (or None if
            no child node was replaced).
        """
        child_name = child_node.name
        old_child = self.attributes[Attributes.CHILDREN].get(child_name)
        self.attributes[Attributes.CHILDREN][child_name] = child_node.attributes

        if old_child is None:
            return None
        else:
            return _node_from_attributes(old_child)

    def _get_child(self, name):
        """
        Returns the child of this directory with the given name.

        Raises:
            KeyError: If no such child exists.
        """
        child_attributes = self.attributes[Attributes.CHILDREN][name]
        return _node_from_attributes(child_attributes)

    def _remove_child(self, name):
        """
        Removes the child (and all of its children, if applicable).

        Returns the removed child node upon success.

        Raises:
            KeyError: If no such child exists.
        """
        children = self.attributes[Attributes.CHILDREN]
        child = children[name]
        del children[name]
        return _node_from_attributes(child)


def _node_from_attributes(attributes):
    """
    Constructs the proper subclass of _Node from the given attributes.
    """
    if Attributes.CHILDREN in attributes:
        return Directory(attributes)
    else:
        return File(attributes)


class Manifest:
    ROOT_DIRECTORY_NAME = ""

    def __init__(self):
        """
        Creates an empty Manifest.
        """
        self.root = Directory.from_values(Manifest.ROOT_DIRECTORY_NAME)

    def __cmp__(self, other):
        """
        Manifests are comparable by their roots.
        """
        return cmp(self.root, other.root)

    def serialize(self):
        """
        Returns:
            The BSON representation of the manifest.
        """
        return bson.dumps(self.root.attributes)

    @staticmethod
    def deserialize(string):
        """
        Args:
            string representation of a Manifest as output by serialize().
        Returns:
            A valid Manifest object if the string can be parsed
        Raises:
            ParseException if the string cannot be parsed
        """
        try:
            attributes = bson.loads(string)
        except Exception:
            raise exceptions.ParseException
        parsed_root = _node_from_attributes(attributes)
        manifest = Manifest()
        manifest.root = parsed_root
        return manifest

    @staticmethod
    def _tokenize_path(path):
        """
        Args:
            path: the path of the node to find, with Directories separated by
                the system delimiter.

        Returns:
            An array of strings representing the directories (and filename
        where applicable) in the given path.
        """
        path = os.path.normpath(path)
        if path is os.curdir:
            return []

        path_tokens = []
        while len(path) > 0:
            path, token = os.path.split(path)
            path_tokens.append(token)
        return list(reversed(path_tokens))

    def _find_node(self, path):
        """
        Args:
            path: a path suitable to be passed to _tokenize_path.

        Returns:
            The node at that path or None if the node was not found
        """
        path_nodes = self._tokenize_path(path)

        current_node = self.root
        try:
            for node_name in path_nodes:
                current_node = current_node._get_child(node_name)
            return current_node
        except (AttributeError, KeyError):
            # We tried to find the child of a File or a required child node
            # didn't exist.
            return None

    def get(self, path):
        """
        Args:
            path: true name of the File or Directory to be searched for
        Returns:
            File or Directory object at the given path, if one exists
        Raises:
            InvalidPath if file is not found
        """
        node = self._find_node(path)

        if node is None:
            raise exceptions.InvalidPath

        return node

    def remove(self, path):
        """
        Args:
            path of the file to be removed
        Returns:
            The File or Directory that was removed if it is found
        Raises:
            InvalidPath if path is not found or if an attempt was made to remove
            the root directory
        """
        parent_directory_path, target_name = os.path.split(path)
        parent_node = self.get(parent_directory_path)

        try:
            target_node = parent_node._remove_child(target_name)
            return target_node
        except (KeyError, AttributeError):
            # The parent_node was a file, or didn't have the
            # specified child.
            raise exceptions.InvalidPath

    def update_file(self, path, code_name, size, key):
        """
        Updates the manifest in place with a file.
        If the path already exists as a file, replace its properties.
        Otherwise, create the file node (and any intermediate Directory nodes if
        necessary).

        Args:
            path: the path of the file to create
            code_name: string representing the new file code name
            size: decimal representation of size
            key: byte representation of the encryption key

        Returns:
            The code_name of the specified file before the update (or None if
            this is a new file).

        Raises:
            InvalidPath if there are existing Files or Directories that
            conflict with the given path.
        """
        parent_directory_path, file_name = os.path.split(path)
        if file_name == "":
            raise exceptions.InvalidPath
        else:
            parent_directory = self.create_directory(parent_directory_path)

        new_file = File.from_values(file_name, code_name, size, key)
        old_node = parent_directory._add_child(new_file)

        if type(old_node) is Directory:
            # First revert change
            parent_directory._add_child(old_node)
            raise exceptions.InvalidPath

        return old_node

    def create_directory(self, path):
        """
        Updates the manifest in place with a new Directory (along with any
        required intermediate Directories).  If the directory already exists,
        this function does nothing.

        Args:
            path: the path of the Directory to create

        Returns:
            The newly created Directory object.  If multiple directories or no
            directories were created, returns the directory in the given path
            furthest from the root.

        Raises:
            InvalidPath if there are existing Files that conflict with the
            given path.
        """
        path_tokens = self._tokenize_path(path)

        current_node = self.root
        try:
            while len(path_tokens) > 0:
                node_name = path_tokens.pop(0)
                current_node = current_node._get_child(node_name)
        except KeyError:
            # The most recent token didn't exist as the child of a node, so the
            # remaining nodes must be created.
            path_tokens.insert(0, node_name)  # Replace the first missing node
            for node_name in path_tokens:
                new_directory = Directory.from_values(node_name)
                current_node._add_child(new_directory)
                current_node = new_directory
        except AttributeError:
            # We tried to call _get_child on a File object
            raise exceptions.InvalidPath

        if type(current_node) is not Directory:  # This won't get caught above
            raise exceptions.InvalidPath
        return current_node
