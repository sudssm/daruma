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
        if provider.status == ProviderStatus.RED:
            # bring back to yellow since he's online now
            provider.errors = 1

    def log_success(self):
        """
        Update the providers to reflect a fully successful operation
        """
        for provider in self.providers:
            self._log_provider_success(provider)

    def diagnose(self, failures):
        """
        Update providers to reflect some failures
        Returns True if all provider contained within failures is yellow or green (so we can retry)
        """
        # TODO maybe raise network failure here?
        if failures is None:
            return
        failed_providers = set()
        for failure in failures:
            if type(failure) is exceptions.AuthFailure:
                # don't punish for AuthFailures
                failure.provider.authenticated = False
            else:
                failure.provider.errors += 1
            failed_providers.add(failure.provider)

        all_good = True

        for provider in self.providers:
            if provider not in failed_providers:
                self._log_provider_success(provider)
            if provider.status not in [ProviderStatus.GREEN, ProviderStatus.YELLOW]:
                all_good = False

        return all_good

    # TODO in general, in repairs, we don't have to upload new file if the error was
    # connection failure. if provider is down, we just diagnose and retry til red?
    def diagnose_and_repair_file(self, failures, filename, data):
        """
        diagnose a list of failures, and then try to repair the file
        Args: failures - a list of ProviderFailures
              filename - the filename to replace
              data - the correct value of the file
        Invariant: Upon exit, either the system is stable or at least one provider is red
        """
        can_continue = self.diagnose(failures)

        try:
            # attempt to repair file
            self.file_manager.put(filename, data)
            self.log_success()
        except exceptions.OperationFailure as e:
            # will necessarily happen if the error was due to a missing file
            # because deleting that file will not work. So, ignore all additional
            # from providers in failures
            original_providers = [failure.provider for failure in failures]
            additional_errors = [failure for failure in e.failures if failure.provider not in original_providers]
            if len(additional_errors) > 0:
                self.diagnose(additional_errors)
            else:
                self.log_success()
        except exceptions.FatalOperationFailure as e:
            # unable to repair
            # retry if all providers are not red
            if can_continue:
                return self.diagnose_and_repair_file(e.failures, filename, data)
            self.diagnose(e.failures)

    def diagnose_and_repair_bootstrap(self, failures):
        """
        diagnose a list of failures, and then try to repair the bootstrap
        Invariant: Upon exit, either the system is stable or at least one provider is red
        """
        can_continue = self.diagnose(failures)

        # we need to get the manifest to repair the bootstrap
        try:
            self.file_manager.load_manifest()
            self.log_success()
        except exceptions.OperationFailure as e:
            can_continue = self.diagnose(e.failures)
        except exceptions.FatalOperationFailure as e:
            # can't proceed if unable to load manifest; retry
            if can_continue:
                return self.diagnose_and_repair_bootstrap(e.failures)
            self.diagnose(e.failures)
            return

        master_key = generate_key()
        manifest_name = generate_filename()
        bootstrap = Bootstrap(master_key, manifest_name, self.file_manager.file_reconstruction_threshold)

        try:
            # TODO when we add caching
            # TODO what if part of this distribute fails? need to rollback or invalidate cache
            # TODO what if manifest upload encounters network error -- then cached manifest is incorrect
            # TODO ensure that this is actually atomic
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.bootstrap_manager.distribute_bootstrap(bootstrap)
        except exceptions.FatalOperationFailure as e:
            # retry if all providers are not red
            if can_continue:
                return self.diagnose_and_repair_bootstrap(e.failures)
            self.diagnose(e.failures)

    def garbage_collect(self):
        # TODO
        # requires provider ls support
        pass
