class ProviderStatus:
    """
    Status codes to report to the UI
    RED: the provider is currently offline or corrupting
    YELLOW: the provider is currently online, but has experienced difficulties in the recent past
    GREEN: the provider is online and has been performing well
    AUTH_FAIL: the provider is online but it returning auth failures
    """
    RED, YELLOW, GREEN, AUTH_FAIL = "RED", "YELLOW", "GREEN", "AUTH_FAIL"


class BaseProvider(object):
    """
    Stub for a provider
    """
    RED_THRESHOLD = .1
    YELLOW_THRESHOLD = .95

    @staticmethod
    def load_cached_providers(credential_manager):
        """
        Attempts to load all Providers of this type that have user credential stored
        Returns:
            (providers, failed_identifiers)
            providers: a list of functional Providers
            failed_identifiers: a list of identifiers for the accounts that failed to load
        """
        raise NotImplementedError

    def __init__(self, credential_manager):
        """
        Set up the provider
        To be called by all implementing classes
        Args: credential_manager, a credential_manager to store user credentials
        """
        self.credential_manager = credential_manager
        # metadata for diagnosis
        # TODO maybe factor this out into a provider manager?
        # TODO maybe get this score from a cached file if available?
        self.score = 1
        self.error_log = []

        # whether the system is currently authenticated
        self.authenticated = True
        # whether we recommend this provider be removed
        # TODO
        self.recomend_removal = False

    def get(self, filename):
        """
        Gets a file from the provider
        Args: filename, the file to retrieve
        Raises: ProviderOperationFailure if unable to retrieve file
        """
        raise NotImplementedError

    def put(self, filename, data):
        """
        Puts a file on the provider
        Args: filename, the file to put
              data, the content of the file
        Raises: ProviderOperationFailure if unable to put file
        """
        raise NotImplementedError

    def get_capacity(self):
        """
        Get quota and capacity information
        Raises: ProviderOperationFailure if unable to get information
        Returns:
            (used_space, total_allocated_space)
            used_space: The amount of space used
            total_allocated_space: The total usable space
        """
        raise NotImplementedError

    def delete(self, filename):
        """
        Deletes a file from the provider
        Args: filename, the file to delete
        Raises: ProviderOperationFailure if unable to delete file
        """
        raise NotImplementedError

    def wipe(self):
        """
        Delete all files on the provider
        Raises ProviderOperationFailure if unable to wipe
        """
        raise NotImplementedError

    # TODO ls?

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
        if self.score < self.RED_THRESHOLD:
            return ProviderStatus.RED
        if self.score < self.YELLOW_THRESHOLD:
            return ProviderStatus.YELLOW
        return ProviderStatus.GREEN

    @staticmethod
    def provider_name():
        """
        Returns a pretty-printed identifier for this type of provider. Must be unique across all provider types
        """
        raise NotImplementedError

    @property
    def uid(self):
        """
        Returns an identifier for this provider. Must be unique across all providers of this type.
        """
        raise NotImplementedError

    @property
    def uuid(self):
        """
        Returns a globally unique identifier for the provider.
        Of the form (provider type, provider id)
        """
        return (self.provider_name(), self.uid)

    def __str__(self):
        return "<" + self.provider_name() + "@" + self.uid + "-" + str(self.score) + ">"
