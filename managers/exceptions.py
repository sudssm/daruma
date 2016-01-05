# Custom Exceptions

class ProvidersDown(Exception):
  pass
class ProvidersUnconfigured(Exception):
  pass

# manifest exceptions
class InvalidFormatException(Exception):
    pass
class IllegalArgumentException(Exception):
    pass
