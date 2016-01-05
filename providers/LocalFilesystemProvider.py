import errno
import os
import shutil
from providers.BaseProvider import BaseProvider, ProviderFileNotFound

DIRECTORY_MODE = 0o700  # RW only for current user


class LocalFilesystemProvider(BaseProvider):
    def __init__(self, provider_path=""):
        """
        Initialize a non-networked provider backed by the local filesystem.

        Args:
            provider_path: an optional string holding the relative or absolute base path for the backing directory on the filesystem.  Defaults to the current directory.
        """
        self.provider_path = provider_path
        super(LocalFilesystemProvider, self).__init__()

    def __get_translated_filepath(self, relative_filename):
        return os.path.join(self.provider_path, self.root_dir, relative_filename)

    def setup(self):
        try:
            translated_root_dir = self.__get_translated_filepath("")
            os.makedirs(translated_root_dir, DIRECTORY_MODE)
        except OSError as error:
            if error.errno is not errno.EEXIST:
                raise

    def connect(self):
        self.setup()
        pass  # Does nothing - we're always connected to the filesystem!

    def get(self, filename):
        translated_filepath = self.__get_translated_filepath(filename)
        try:
            with open(translated_filepath, mode="rb") as target_file:
                return target_file.read()
        except IOError as error:
            if error.errno is errno.ENOENT:
                raise ProviderFileNotFound
            else:
                raise

    def put(self, filename, data):
        translated_filepath = self.__get_translated_filepath(filename)
        with open(translated_filepath, mode="wb") as target_file:
            target_file.write(data)

    def delete(self, filename):
        translated_filepath = self.__get_translated_filepath(filename)
        try:
            os.remove(translated_filepath)
        except OSError as error:
            if error.errno is errno.ENOENT:
                raise ProviderFileNotFound
            else:
                raise

    def wipe(self):
        translated_root_dir = self.__get_translated_filepath("")
        try:
            shutil.rmtree(translated_root_dir)
            os.makedirs(translated_root_dir, DIRECTORY_MODE)
        except Exception:
            raise
