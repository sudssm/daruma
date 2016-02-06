# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from tools.utils import generate_name
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
        # self.get_manifest()

    def get_manifest(self):
        try:
            manifest_str, failures = self.distributor.get(self.manifest_name, self.master_key)
        except exceptions.FileReconstructionError:
            raise exceptions.ManifestGetError

        # TODO: deal with failures
        # if len(failures) == len(providers) and all(failures.values() are ConnectionError)
        # raise NetworkError

        if manifest_str is None:
            raise exceptions.ManifestGetError

        self.manifest = Manifest(content=manifest_str)

    def distribute_manifest(self):
        content = str(self.manifest)
        _, failures = self.distributor.put(self.manifest_name, content, self.master_key)
        # TODO handle failures - will be passed up

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
        self.get_manifest()
        return self.manifest.ls()

    def put(self, name, data):
        self.get_manifest()
        codename = generate_name()
        key, failures = self.distributor.put(codename, data)
        # TODO handle failed_providers
        # early return if this fails

        old_codename = self.manifest.update_manifest(name, codename, len(data), key)

        # update the manifest
        self.distribute_manifest()

        if old_codename is not None:
            self.distributor.delete(old_codename)

    def get(self, name):
        self.get_manifest()
        entry = self.manifest.get_line(name)

        codename = entry["code_name"]
        key = entry["aes_key"]

        result, failures = self.distributor.get(codename, key)
        # TODO: used failures
        return result

    def delete(self, name):
        self.get_manifest()
        entry = self.manifest.remove_line(name)

        self.distribute_manifest()
        self.distributor.delete(entry["code_name"])
