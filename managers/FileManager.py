# This file handles files using RS
# this thingy should also eventually handle striping
from custom_exceptions import exceptions
from Distributor import FileDistributor
from manifest import Manifest
from uuid import uuid4


class FileManager:
    # the name of the manifest file
    MANIFEST_NAME = "manifest"

    def __init__(self, providers, file_reconstruction_threshold, master_key):
        self.providers = providers
        self.file_reconstruction_threshold = file_reconstruction_threshold
        self.master_key = master_key
        self.distributor = FileDistributor(providers, file_reconstruction_threshold)

        self.get_manifest()

    def get_manifest(self):
        # get shares from providers in parallel
        # once we have k shares, un-RS the manifest
        # decrypt the manifest
        # parse the manifest

        # if there were providers that didn't have shares of the manifest
        # (or had invalid shares of the manifest):
        #   self.refresh()

        try:
            manifest_str = self.distributor.get(self.MANIFEST_NAME, self.master_key)
            self.manifest = Manifest(content=manifest_str)  # TODO: handle possible IllegalArgument
        except exceptions.FileNotFound:
            # make a new manifest and distribute it
            self.manifest = Manifest()
            self.distribute_manifest()

    def distribute_manifest(self):
        content = str(self.manifest)
        self.distributor.put(self.MANIFEST_NAME, content, self.master_key)

    def refresh(self):
        pass
        # for every file, perform a self.get() and self.put()
        # to fetch it, re-encode it with the new list of providers, and put it
        # used most often for reprovisioning new or broken provider

    def ls(self):
        return self.manifest.ls()

    def put(self, name, data):
        codename = str(uuid4()).replace('-', '').upper()
        (key, reached_threshold, failed_providers_map) = self.distributor.put(codename, data)
        # TODO len(data) probably isn't good enough for file size
        # should maybe make a class for a file
        old_codename = self.manifest.update_manifest(name, codename, len(data), key)

        # update the manifest
        self.distribute_manifest()

        if old_codename is not None:
            self.distributor.delete(old_codename)

    def get(self, name):
        entry = self.manifest.get_line(name)

        if entry is None:
            return None

        codename = entry["code_name"]
        key = entry["aes_key"]

        try:
            return self.distributor.get(codename, key)
        except exceptions.FileNotFound:
            # TODO: throw an exception when this occurs because
            # this situation implies that we expected to see
            # a file with the given codename and but cannot retrieve shares
            # which is "bad news bears" indeed
            return None

    def delete(self, name):
        entry = self.manifest.remove_line(name)
        if entry is None:
            return
        self.distribute_manifest()
        self.distributor.delete(entry["code_name"])
