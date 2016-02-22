# stub for a provider
# interface that allows cloud and local providers


class ProviderStatus:
    RED, YELLOW, GREEN = "RED", "YELLOW", "GREEN"


class BaseProvider(object):
    # the path to our files on the cloud provider
    ROOT_DIR = "secretbox"

    def __init__(self):
        # this function will not be overridden
        # but rather called by other constructors that take parameters

        # TODO change this when diagnose becomes more sophisticated
        self.errors = 0
        self.error_log = []
        self.connect()

    # can throw ConnectionFailure, AuthFailure
    def connect(self):
        # connect to the cloud provider and make sure it is alive
        # throw an exception if it isn't
        pass

    # the rest of these should only throw ProviderOperationFailure
    def get(self, filename):
        pass

    def put(self, filename, data):
        pass

    def delete(self, filename):
        pass

    def wipe(self):
        """
        Delete all files on the provider
        """

    def log_error(self, exception):
        self.error_log.append(exception)

    @property
    def status(self):
        if self.errors > 20:
            return ProviderStatus.RED
        if self.errors > 1:
            return ProviderStatus.YELLOW
        return ProviderStatus.GREEN
