# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from uuid import uuid4
# TODO cache the manifest intelligently


class FileManager:
    # the name of the manifest file
    MANIFEST_NAME = "manifest"

    # set setup to True in order to create a new system
    def __init__(self, providers, file_reconstruction_threshold, master_key, setup=False):
        self.providers = providers
        self.file_reconstruction_threshold = file_reconstruction_threshold
        self.master_key = master_key
        self.distributor = FileDistributor(providers, file_reconstruction_threshold)

        if setup:
            self.manifest = Manifest()
            self.distribute_manifest()
        # else:
        # self.get_manifest()

    def get_manifest(self):
        try:
            manifest_str, failed_providers_map = self.distributor.get(self.MANIFEST_NAME, self.master_key)
        except exceptions.FileReconstructionError:
            raise exceptions.ManifestGetError

        # TODO: deal with failed_providers_map
        # if len(failed_providers_map) == len(providers) and all(failed_providers_map.values() are ConnectionError)
        # raise NetworkError

        if manifest_str is None:
            raise exceptions.ManifestGetError

        self.manifest = Manifest(content=manifest_str)

    def distribute_manifest(self):
        content = str(self.manifest)
        _, failed_providers_map = self.distributor.put(self.MANIFEST_NAME, content, self.master_key)
        # TODO handle failed_providers_map

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
        codename = str(uuid4()).replace('-', '').upper()
        key, failed_providers_map = self.distributor.put(codename, data)
        # TODO handle failed_providers

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

        result, failed_providers_map = self.distributor.get(codename, key)
        # TODO: used failed_providers_map
        return result

    def delete(self, name):
        self.get_manifest()
        entry = self.manifest.remove_line(name)

        self.distribute_manifest()
        self.distributor.delete(entry["code_name"])
