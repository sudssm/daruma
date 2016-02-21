from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename
from managers.BootstrapManager import Bootstrap


class ResilienceManager:
    def __init__(self, providers, file_manager, bootstrap_manager):
        self.file_manager = file_manager
        self.bootstrap_manager = bootstrap_manager
        self.providers = providers

    def log_success(self):
        # TODO
        # to be called when all providers responded correctly
        for provider in self.providers:
            pass

    def diagnose(self, failures):
        # TODO ignore auth failures; raise them?
        # TODO maybe raise network failure here?
        # TODO
        for failure in failures:
            failure.provider.log_error(failure)
            failure.provider.errors += 1
            if failure.provider.errors > 50:
                raise exceptions.RedProviderFailure


    # TODO in general, in repairs, we don't have to upload new file if the error was
    # connection failure. if provider is down, we just diagnose and retry til red?
    def diagnose_and_repair_file(self, failures, filename, data):
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
            # unable to repair; try again
            self.diagnose_and_repair_file(e.failures, filename, data)

    def diagnose_and_repair_bootstrap(self, failures):
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
            # TODO what if part of this distribute fails? need to rollback
            # TODO ensure that this is actually atomic
            self.file_manager.update_key_and_name(master_key, manifest_name)
            self.bootstrap_manager.distribute_bootstrap(bootstrap)
        except exceptions.FatalOperationFailure as e:
            self.diagnose_and_repair_bootstrap(e.failures)

    def diagnose_and_repair_entry(self):
        # for the bootstrap_reconstruction_threshold
        # TODO
        # maybe we don't need this; bootstrap manager distribute sort of takes care of it
        pass
