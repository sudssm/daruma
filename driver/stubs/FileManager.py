# This file handles files using RS
# this thingy should also eventually handle striping
import exceptions


class FileManager:

    def __init__(self, providers, k_file, master_key):
        self.providers = providers
        self.k = k_file
        self.master_key = master_key

        self.get_manifest()

    def get_manifest(self):
        # get shares from providers in parallel
        # once we have k shares, un-RS the manifest
        # decrypt the manifest
        # parse the manifest

        # if there were providers that didn't have shares of the manifest
        # (or had invalid shares of the manifest):
        #   self.refresh()
        pass

    def distribute_manifest(self):
        # encrypt the manifest
        # compute RS new shares for the manifest
        # distribute the shares to all providers

        # called when the provider list is inconsistent with the state of the providers
        pass

    def refresh(self):
        self.distribute_manifest()
        # for every file, perform a self.get() and self.put()
        # to fetch it, re-encode it with the new list of providers, and put it

    def ls(self):
        manifest = self.get_manifest()
        manifest.ls()

    def get_file(self, path, f_key):
        # check manifest for path; get random file name
        manifest = self.get_manifest()
        attributes = manifest.get_line(path)

        # fetch random file name in parallel from providers
        for provider in self.providers:
            pass  # get file using attributes[random_name]

        # once we have enough shares, un-RS it
        # decrypt
        pass

    def distribite_file(self, path, f_key, data):
        # compute RS shares of the file
        # create a random name for the file
        # upload RS shares to the random name for all providers
        # update the manifest with the path,random_name pair
        # self.distribute_manifest()
        # if we just replaced a file (instead of putting a fresh one)
        #   delete the old random_name files from all providers
        pass

    def delete_file(self, path):
        # lookup the path in the manifest
        # update the manifest
        # self.distribute_manifest()
        # delete the old random_name files from all providers
        pass
