from custom_exceptions import exceptions
from tools.encryption import generate_key
from tools.utils import generate_filename
from managers.BootstrapManager import Bootstrap


class ResilienceManager:
    def __init__(self, providers, file_manager, bootstrap_manager):
        self.file_manager = file_manager
        self.bootstrap_manager = bootstrap_manager
        pass

    def log_success(self):
        # to be called when all providers responded correctly
        pass

    def diagnose(self, failures):
        print "*** diagnose"
        # assign failing providers bad scores based on the failures
        for failure in failures:
            print failure
        # TODO

    def diagnose_and_repair_file(self, failures, filename, data):
        print "FILE failures"
        self.diagnose(failures)

        try:
            # attempt to repair file
            self.file_manager.put(filename, data)
        except exceptions.OperationFailure as e:
            # necessarily going to happen because delete of the old filename will fail
            # TODO remove all of the providers in failures from e.failures
            # if there are any left, diagnose them
            pass
        except exceptions.FatalOperationFailure as e:
            # unable to repair; update diagnosis and return
            self.diagnose(e.failures)

    def diagnose_and_repair_bootstrap(self, failures):
        print "BOOTSTRAP failures"

        # we need to get the manifest to repair the bootstrap
        try:
            self.file_manager.load_manifest()
        except exceptions.OperationFailure as e:
            failures += e.failures
        except exceptions.FatalOperationFailure:
            # TODO diagnose?
            raise

        self.diagnose(failures)

        # TODO maybe refactor this?
        master_key = generate_key()
        manifest_name = generate_filename()
        bootstrap = Bootstrap(master_key, manifest_name, self.file_manager.file_reconstruction_threshold)

        # TODO what if manifest distribute fails? need to rollback
        # TODO try/catch
        self.file_manager.update_key_and_name(master_key, manifest_name)
        self.bootstrap_manager.distribute_bootstrap(bootstrap)

    def diagnose_and_repair_entry(self):
        # for the bootstrap_reconstruction_threshold
        # TODO
        # maybe we don't need this; bootstrap manager distribute sort of takes care of it
        pass
