import errno
import os
import shutil
from tools.utils import APP_NAME
from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider

DIRECTORY_MODE = 0o700  # RW only for current user


class LocalFilesystemProvider(BaseProvider):
    def __init__(self, provider_path=""):
        """
        Initialize a non-networked provider backed by the local filesystem.

        Args:
            provider_path: an optional string holding the relative or
                absolute base path for the backing directory on the filesystem.
                Defaults to the current directory.
        """
        super(LocalFilesystemProvider, self).__init__()
        self.ROOT_DIR = APP_NAME
        self.provider_path = provider_path
        self._connect()

    def _get_translated_filepath(self, relative_filename):
        return os.path.join(self.provider_path, self.ROOT_DIR, relative_filename)

    def _connect(self):
        try:
            translated_root_dir = self._get_translated_filepath("")
            os.makedirs(translated_root_dir, DIRECTORY_MODE)
        except (IOError, OSError) as error:
            if error.errno is not errno.EEXIST:
                raise exceptions.ConnectionFailure(self)

    def get(self, filename):
        translated_filepath = self._get_translated_filepath(filename)
        try:
            with open(translated_filepath, mode="rb") as target_file:
                return target_file.read()
        except (IOError, OSError):
            raise exceptions.ProviderOperationFailure(self)

    def put(self, filename, data):
        translated_filepath = self._get_translated_filepath(filename)
        try:
            with open(translated_filepath, mode="wb") as target_file:
                target_file.write(data)
        except (IOError, OSError):
            raise exceptions.ProviderOperationFailure(self)

    def delete(self, filename):
        translated_filepath = self._get_translated_filepath(filename)
        try:
            os.remove(translated_filepath)
        except (IOError, OSError):
            raise exceptions.ProviderOperationFailure(self)

    def wipe(self):
        translated_root_dir = self._get_translated_filepath("")
        try:
            shutil.rmtree(translated_root_dir)
            os.makedirs(translated_root_dir, DIRECTORY_MODE)
        except (IOError, OSError):
            raise exceptions.ProviderOperationFailure(self)
