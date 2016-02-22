from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename
from managers.BootstrapManager import Bootstrap
from providers.BaseProvider import ProviderStatus


class ResilienceManager:
    def __init__(self, providers, file_manager, bootstrap_manager):
        """
        Construct a ResilienceManager
        """
        self.file_manager = file_manager
        self.bootstrap_manager = bootstrap_manager
        self.providers = providers

    def _log_provider_success(self, provider):
        """
        Update the provider to reflect a successful operation
        """
        # TODO

    def log_success(self):
        """
        Update the providers to reflect a fully successful operation
        """
        for provider in self.providers:
            self._log_provider_success(provider)

    def diagnose(self, failures):
        """
        Update providers to reflect some failures
        """
        # TODO ignore auth failures; raise them? update provider status to AuthFail
        # TODO maybe raise network failure here?
        # TODO update providers not contained in failures to reflect successful operation
        failed_providers = set()
        for failure in failures:
            failure.provider.errors += 1
            failed_providers.add(failure.provider)
        for provider in self.providers:
            if provider not in failed_providers:
                self._log_provider_success(provider)

    def _has_red_provider(self, failures):
        """
        Returns True if any provider contained within failures is red
        """
        for failure in failures:
            if failure.provider.status == ProviderStatus.RED:
                return True
        return False

    # TODO in general, in repairs, we don't have to upload new file if the error was
    # connection failure. if provider is down, we just diagnose and retry til red?
    def diagnose_and_repair_file(self, failures, filename, data):
        """
        diagnose a list of failures, and then try to repair the file
        If a provider repeatedly fails, will continue to attempt repair until red
        Args: filename - the filename to replace
              data - the correct value of the file
        """
        self.diagnose(failures)

        try:
            # attempt to repair file
            self.file_manager.put(filename, data)
        except exceptions.OperationFailure as e:
            # will necessarily happen if the error was due to a missing file
            # because deleting that file will not work. So, ignore all additional
            # from providers in failures
            original_providers = [failure.provider for failure in failures]
            additional_errors = [failure for failure in e.failures if failure.provider not in original_providers]
            if len(additional_errors) > 0:
                self.diagnose(additional_errors)
        except exceptions.FatalOperationFailure as e:
            # unable to repair
            # if a provider is now red, just diagnose and stop
            if self._has_red_provider(e.failures):
                self.diagnose(e.failures)
            # otherwise retry
            else:
                self.diagnose_and_repair_file(e.failures, filename, data)

    def diagnose_and_repair_bootstrap(self, failures):
        """
        diagnose a list of failures, and then try to repair the bootstrap
        If a provider repeatedly fails, will continue to attempt repair until red
        """
        self.diagnose(failures)

        # we need to get the manifest to repair the bootstrap
        try:
            self.file_manager.load_manifest()
        except exceptions.OperationFailure as e:
            self.diagnose(e.failures)
        except exceptions.FatalOperationFailure as e:
            # can't proceed if unable to load manifest; retry
            self.diagnose_and_repair_bootstrap(e.failures)

        master_key = generate_key()
        manifest_name = generate_filename()
        bootstrap = Bootstrap(master_key, manifest_name, self.file_manager.file_reconstruction_threshold)

        try:
            # TODO when we add caching
            # TODO what if part of this distribute fails? need to rollback or invalidate cache
            # TODO what if manifest upload encounter network error -- then cached manifest is broken
            # TODO ensure that this is actually atomic
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.bootstrap_manager.distribute_bootstrap(bootstrap)
        except exceptions.FatalOperationFailure as e:
            # unable to repair
            # if a provider is now red, just diagnose and stop
            if self._has_red_provider(e.failures):
                self.diagnose(e.failures)
            # otherwise retry
            else:
                self.diagnose_and_repair_bootstrap(e.failures)

    def garbage_collect(self):
        # TODO
        pass
