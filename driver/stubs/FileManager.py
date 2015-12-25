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

  def distribute_manifest(self):
    # encrypt the manifest
    # compute RS new shares for the manifest
    # distribute the shares to all providers

  # called when the provider list is inconsistent with the state of the providers
  def refresh(self):
    self.distribute_manifest()
    # for every file, perform a self.get() and self.put()
    # to fetch it, re-encode it with the new list of providers, and put it

  def ls (self):
    # just look at the manifest
    
  def get(self, path):
    # check manifest for path; get random file name
    # fetch random file name in parallel from providers
    # once we have enough shares, un-RS it
    # decrypt
  
  def put(self, path, data):
    # compute RS shares of the file
    # create a random name for the file
    # upload RS shares to the random name for all providers
    # update the manifest with the path,random_name pair
    # self.distribute_manifest()
    # if we just replaced a file (instead of putting a fresh one)
    #   delete the old random_name files from all providers
  
  def delete(self, path):
    # lookup the path in the manifest
    # update the manifest
    # self.distribute_manifest()
    # delete the old random_name files from all providers
  
