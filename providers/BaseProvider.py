from tools.utils import APP_NAME
from custom_exceptions import exceptions
from tools.utils import run_parallel


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
    RED_THRESHOLD = .5
    YELLOW_THRESHOLD = .95

    ROOT_DIR = APP_NAME

    @classmethod
    def load_from_credential(cls, credential_manager, provider_id):
        """
        Attempts to load a single provider with provider_id from the supplied credential manager
        """
        raise NotImplementedError

    @classmethod
    def load_cached_providers(cls, credential_manager):
        """
        Attempts to load all Providers of this type that have user credential stored
        Returns:
            (providers, failed_identifiers)
            providers: a list of functional Providers
            failed_identifiers: a list of uuids for the accounts that failed to load
        """
        providers = []
        failed_ids = []

        def run_load(provider_id):
            try:
                provider = cls.load_from_credential(credential_manager, provider_id)
                providers.append(provider)
            except:
                failed_ids.append((cls.provider_identifier(), provider_id))

        credentials = credential_manager.get_user_credentials(cls)
        run_parallel(run_load, map(lambda provider_id: [provider_id], credentials.keys()))

        return providers, failed_ids

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

    @classmethod
    def provider_identifier(cls):
        """
        Returns a string for this provider. Must be unique across all provider
        types.
        This will not be displayed, but will be used in the following scenarios:
            - The provider logo will be assumed to be called
              <provider_identifier>.png
            - The identifier may be used in various internal indexes and URLs.
        """
        return NotImplementedError

    @classmethod
    def provider_name(cls):
        """
        Returns a pretty-printed identifier for this type of provider. Must be
        unique across all provider types.
        If no provider logo is provided, this will be rendered in its place in
        the GUI.
        """
        raise NotImplementedError

    @property
    def uid(self):
        """
        Returns an identifier for this provider. Must be unique across all
        providers of this type.  This identifier will be user-facing, so an
        account username or file path would be a good candidate.
        """
        raise NotImplementedError

    @property
    def uuid(self):
        """
        Returns a globally unique identifier for the provider.
        Of the form (provider type, provider id)
        """
        return (self.provider_identifier(), self.uid)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __hash__(self):
        return self.uuid.__hash__()

    def __str__(self):
        return "<" + self.provider_name() + "@" + self.uid + "-" + str(self.score) + ">"

    def remove(self):
        """
        Clears the provider and removes its credentials from the system.
        The provider will be unusable after calling this function.
        """
        try:
            self.wipe()
        except exceptions.ProviderFailure:
            pass
        self.credential_manager.clear_user_credentials(self.__class__, self.uid)
