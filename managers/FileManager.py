# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from tools.utils import generate_filename
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
            self.manifest = Manifest(content=manifest_str)
        except exceptions.OperationFailure as e:
            # set manifest to recovered value and pass along failures
            self.manifest = Manifest(content=e.result)
            raise exceptions.OperationFailure(e.failures, None)

        # TODO: deal with failures
        # if len(failures) == len(providers) and all(failures.values() are ConnectionError)
        # raise NetworkError - handle one level up?

    def distribute_manifest(self):
        """
        Raises FatalOperationFailure if any provider fails
        """
        content = str(self.manifest)
        self.distributor.put(self.manifest_name, content, self.master_key)

    def update_key_and_name(self, master_key, manifest_name):
        self.master_key = master_key
        self.manifest_name = manifest_name
        self.distribute_manifest()
        # TODO make sure this doesnt go to infinite loop on repeated distributes

    def refresh(self):
        pass
        # for every file, perform a self.get() and self.put()
        # to fetch it, re-encode it with the new list of providers, and put it
        # used most often for reprovisioning new or broken provider

    def ls(self):
        # TODO note that this will change once we start intelligently caching manifests
        try:
            # can't raise, since we need to allow reads even if a provider is down
            # instead, we combine the exceptions
            self.load_manifest()
        except exceptions.OperationFailure as e:
            # pass up failures
            raise exceptions.OperationFailure(e.failures, self.manifest.ls())

        return self.manifest.ls()

    def put(self, name, data):
        """
        Raises FatalOperationFailure if any provider operation throws an exceptions
        """
        # if this fails, we raise up the error; system is read-only if any provider is down
        self.load_manifest()
        codename = generate_filename()
        key = self.distributor.put(codename, data)

        old_codename = self.manifest.update_manifest(name, codename, len(data), key)

        # update the manifest
        self.distribute_manifest()

        if old_codename is not None:
            self.distributor.delete(old_codename)

    def get(self, name):
        """
        attempt to get a file
        Returns file contents
        Raises FileNotFound if file does not exist
        Raises OperationFailure with errors and file contents if recoverable
        Raises FatalOperationFailure if unrecoverable
        """
        # TODO note that this will change once we start intelligently caching manifests
        failures = []
        try:
            # can't raise, since we need to allow reads even if a provider is down
            # instead, we combine the exceptions
            self.load_manifest()
        except exceptions.OperationFailure as e:
            # keep track of the exceptions
            failures = e.failures

        entry = self.manifest.get_line(name)

        codename = entry["code_name"]
        key = entry["aes_key"]

        try:
            data = self.distributor.get(codename, key)
        except exceptions.OperationFailure as e:
            data = e.result
            failures += e.failures

        if len(failures) > 0:
            raise exceptions.OperationFailure(failures, e.result)

        return data

    def delete(self, name):
        self.load_manifest()
        entry = self.manifest.remove_line(name)

        self.distribute_manifest()
        try:
            self.distributor.delete(entry["code_name"])
        except exceptions.FatalOperationFailure as e:
            # some provider deletes failed, but it wasn't fatal
            raise exceptions.OperationFailure(e.failures, None)
