# Custom Exceptions

class FileNotFound(Exception):
  pass
class ConnectionError(Exception):
  pass

class ProvidersDown(Exception):
  pass
class ProvidersUnconfigured(Exception):
  pass