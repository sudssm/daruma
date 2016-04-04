import errno
import os
import shutil
from tools.utils import APP_NAME
from custom_exceptions import exceptions
from providers.BaseProvider import BaseProvider

DIRECTORY_MODE = 0o700  # RW only for current user


class LocalFilesystemProvider(BaseProvider):
    @staticmethod
    def load_cached_providers(credential_manager):
        credentials = credential_manager.get_user_credentials(__name__)
        providers = []
        failed_paths = []
        for provider_path in credentials.keys():
            try:
                providers.append(LocalFilesystemProvider(credential_manager, provider_path))
            except:
                failed_paths.append(provider_path)
        return providers, failed_paths

    def __init__(self, credential_manager, provider_path=""):
        """
        Initialize a non-networked provider backed by the local filesystem.

        Args:
            credential_manager, a credential_manager to store user credentials
            provider_path: an optional string holding the relative or
                absolute base path for the backing directory on the filesystem.
                Defaults to the current directory.
        """
        super(LocalFilesystemProvider, self).__init__(credential_manager)
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
        self.credential_manager.set_user_credentials(__name__, self.provider_path, None)

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

    @property
    def expose_to_client(self):
        return True
