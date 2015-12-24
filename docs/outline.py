# This is pseudocode for the main project

###############
#Main:

class DoronBox:
  
  def __init__(self):
    # constructor
    # should somehow take in info about cloud providers, either as preconnected objects or a text file with info
    # need to factor out pseudocode below into separate methods
    # somhow connect to all cloud providers
    # -- might be worth factoring out to a different class/piece
    # attempt to un-SSS master key; throw error if unsuccessful
    # keep note of the providers had no or malformed master key share - consider these unconfigured
    # at some point, should add these unconfigured servers
    
    # recover encrypted manifest from some server, decrypt it with master key
    # either keep decrypted manifest in memory or store it somewhere temporary to allow freeing memory
    pass
  
  def ls (self):
    # easy - just look at manifest and print stuff
    pass
    
  def get(self, filename):
    pass
  
  def put(self, filename, data):
    # 2 cases - if file already exists, perform update
    # if not, perform put for new file
    pass
  
  def delete(self, filename):
    pass
  
  