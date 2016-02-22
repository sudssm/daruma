# stub for a provider
# interface that allows cloud and local providers


class ProviderStatus:
    """
    Status codes to report to the UI
    RED: the provider is currently offline or corrupting
    YELLOW: the provider is currently online, but has experienced difficulties in the past
    GREEN: the provider is online and has been performing well
    AUTH_FAIL: the provider is online but it returning auth failures
    """
    RED, YELLOW, GREEN, AUTH_FAIL = "RED", "YELLOW", "GREEN", "AUTH_FAIL"


class BaseProvider(object):
    # the path to our files on the cloud provider
    ROOT_DIR = "secretbox"

    def __init__(self):
        # this function will not be overridden
        # but rather called by other constructors that take parameters

        # metadata for diagnosis
        # TODO maybe factor this out into a provider manager?
        # TODO change this when diagnose becomes more sophisticated
        self.errors = 0
        self.error_log = []

        # whether the system is currently authenticated
        self.authenticated = True
        # whether we recommend this provider be removed
        # TODO
        self.recomend_removal = False

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
        """
        Store an error for internal logging use
        """
        # TODO probably should log more useful information
        self.error_log.append(exception)

    @property
    def status(self):
        """
        Get the current status of the provider
        Returns AUTH_FAIL if the provider needs to be reauthenticated
        Returns RED if the provider is currently misbehaving
        Returns YELLOW if the provider has a history of misbehaving
        Returns GREEN if all is well
        """
        if not self.authenticated:
            return ProviderStatus.AUTH_FAIL
        if self.errors > 20:
            return ProviderStatus.RED
        if self.errors > 0:
            return ProviderStatus.YELLOW
        return ProviderStatus.GREEN
