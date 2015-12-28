# stub for a provider
# interface that allows cloud and local providers
import exceptions

class Provider(object):
  def __init__(self):
    # this function will not be overridden
    # but rather called by other constructors that take parameters

    # the path to our files on the cloud provider
    self.root_dir = "secretbox"
    self.connect()

  def connect(self):
    # connect to the cloud provider and make sure it is alive
    # throw an exception if it isn't
    pass

  def get(self, filename):
    pass

  def put(self, filename, data):
    pass

  def delete(self, filename):
    pass

# stub implementation of a 'cloud provider' on localdisk
class LocalProvider (Provider):
  def __init__(self, path):
    self.path = path
    super(LocalProvider, self).__init__()

  def connect(self):
    # check if the directory exists
    # if yes, then we are 'connected'
    # otherwise throw a ConnectionError
    pass

p = LocalProvider("~/test")