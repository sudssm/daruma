import errno
import os
from driver.provider import Provider
from driver.provider import ProviderFileNotFound

DIRECTORY_MODE = 0o700  # RW only for current user


class LocalFilesystemProvider(Provider):
    def setup(self):
        try:
            os.mkdir(self.root_dir, DIRECTORY_MODE)
        except OSError as error:
            if error.errno is not errno.EEXIST:
                raise

    def connect(self):
        pass

    def get(self, filename):
        translated_filepath = os.path.join(self.root_dir, filename)
        try:
            with open(translated_filepath, mode="rb") as target_file:
                return target_file.read()
        except IOError as error:
            if error.errno is errno.ENOENT:
                raise ProviderFileNotFound
            else:
                raise

    def put(self, filename, data):
        translated_filepath = os.path.join(self.root_dir, filename)
        with open(translated_filepath, mode="wb") as target_file:
            target_file.write(data)

    def delete(self, filename):
        translated_filepath = os.path.join(self.root_dir, filename)
        try:
            os.remove(translated_filepath)
        except OSError as error:
            if error.errno is errno.ENOENT:
                raise ProviderFileNotFound
            else:
                raise
