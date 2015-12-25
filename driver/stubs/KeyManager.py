# This file handles keys using SSSS

import exceptions

class KeyManager:
  KEY_FILE_NAME = "the-name-of-our-key-file"

  def __init__(self, providers, k_key):
    self.providers = providers
    self.k = k

  # un SSSS the key from the providers
  # returns the recovered key from all the shares
  # throws ProvidersUnconfigured if no provider has a keyshare
  # throws ProvidersDown if not enough providers have keyshares
  # probably should throw some sort of connection exception too
  def recover_key(self):
    # get all shares from providers in parallel
    # attempt to recover key
    # if there were providers that had missing or invalid shares
    #   self.distribute_key(key)
    return "1234"

  # distributes the key to all providers
  # probably throws exception if the provider's put method fails
  def distribute_key(self, key):
    # compute new shares using len(providers) and k_key
    # write shares to providers
    pass

  # creates a fresh master key
  def create_key(self):
    return "1234"
