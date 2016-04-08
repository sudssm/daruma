"""
Command line interface for Daruma
"""
from providers.TestProvider import TestProviderState
from providers.BaseProvider import ProviderStatus
from managers.ProviderManager import ProviderManager
from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from contextlib import contextmanager
import traceback
import cmd
import shlex
import colorama


provider_manager = ProviderManager()
providers = []
secret_box = None


@contextmanager
def exception_handler():
    try:
        yield
    except exceptions.FileNotFound:
        print "File does not exist!"
    except exceptions.InvalidPath:
        print "Error: no such file or directory"
    except exceptions.FatalOperationFailure:
        print "Operation Failed! check status"
    except exceptions.ReadOnlyMode:
        print "The system is in read only mode!"
        print "You are missing the following provider:", secret_box.get_missing_providers()
        print "To be able to write, either 'add' more providers, or 'reprovision' with the existing ones."
    except:
        print traceback.format_exc()


def pp_providers():
    return map(lambda provider: provider.uuid, providers)


def add_provider(line):
    line = line.strip().lower()

    if len(line) == 0:
        print "Enter a provider type!"
        return

    line = shlex.split(line)

    provider_type = line[0]

    provider = None

    if provider_type == "dropbox":
        url = provider_manager.start_dropbox_connection()
        print "Visit", url, "to log in to Dropbox"
        localhost_url = raw_input("Enter resulting url (starts with localhost): ")
        with exception_handler():
            provider = provider_manager.finish_dropbox_connection(localhost_url)

    elif provider_type == "local":
        if len(line) < 2:
            print "Usage: add Local <path_name>"
            return
        with exception_handler():
            provider = provider_manager.make_local(line[1])

    elif provider_type == "test":
        if len(line) < 2:
            print "Usage: add Test <path_name>"
            return
        with exception_handler():
            provider = provider_manager.make_test(line[1])

    elif provider_type == "testserver":
        if len(line) < 3:
            print "Usage: add Test <host> <port>"
            return
        with exception_handler():
            provider = provider_manager.make_test_server(line[1], line[2])

    else:
        print "Invalid provider type!"

    if provider is None:
        print "Error loading provider"
        return

    return provider


class ConfigureLoop(cmd.Cmd):
    """
    Configure settings and providers
    """
    prompt = "\nDaruma Configuration> "

    def preloop(self):
        global providers

        print "Welcome to Daruma!"

        # attempt to load cached providers from credentials
        providers, errors = provider_manager.load_all_providers_from_credentials()
        print "Loaded from cache:", pp_providers()
        print "Errors loading from cache:", errors

        if self.do_load():
            print "Press enter to continue"

    def postcmd(self, stop, line):
        print "Loaded providers:", pp_providers()
        # we're done with this section when secretbox is defined
        return secret_box is not None

    def do_add(self, line):
        """
        add <provider type>
        provider_type can be one of "Dropbox", "Local", "Test", "TestServer"
        """
        provider = add_provider(line)
        if provider is None:
            return

        if provider.uuid in pp_providers():
            print provider.uuid, "exists!"
            return

        providers.append(provider)

    def do_load(self, line=None):
        """
        Attempt to load Daruma from the added providers
        """
        global secret_box
        # if we were able to load at least 2 providers, attempt to load an existing instance
        # 2 because we may be trying to load a 3-provider instance in read only mode
        try:
            assert len(providers) >= 2
            secret_box = SecretBox.load(providers)
            print "Loaded an existing installation"
            return True
        except AssertionError:
            print "Looks like you need to add more providers! Type 'add' to get started."
        except exceptions.FatalOperationFailure:
            print "Looks like there's no existing installation with these providers."
            print "If this is correct, type 'provision' to start a new instance. If not, type 'add' to add more providers."
        return False

    def do_provision(self, line=None):
        """
        Attempt to start a new Daruma on the added providers
        """
        global secret_box
        # if we were able to load at least 3 providers, attempt to load an existing instance
        try:
            assert len(providers) >= 3
            threshold = len(providers) - 1
            secret_box = SecretBox.provision(providers, threshold, threshold)
            print "Created a new installation"
        except AssertionError:
            print "Looks like you need to add more providers! Type 'add' to get started."
        except exceptions.FatalOperationFailure as e:
            print "We were unable to create an instance because of errors with", map(lambda failure: failure.provider.uuid, e.failures)


class MainLoop(cmd.Cmd):
    """
    Configure settings and providers
    """
    prompt = "\nDaruma> "

    def preloop(self):
        missing = secret_box.get_missing_providers()
        if len(missing) > 0:
            print "The system is in read only mode!"
            print "You are missing the following provider:", missing
            print "To be able to write, either 'add' more providers, or 'reprovision' with the existing ones."

    def do_ls(self, target):
        """
        ls [target]
        """
        with exception_handler():
            files = secret_box.ls(target)

            if len(files) == 0:
                print "EMPTY"
            for item in files:
                is_dir = item['is_directory']
                print "DIR" if is_dir else "" + str(item['size']),
                print "\t" + item['name']

    def do_mv(self, line):
        """
        mv <old_path> <new_path>
        """
        line = shlex.split(line)
        if len(line) < 2:
            print "Usage: mv <old_path> <new_path>"
            return

        old_path = line[0]
        new_path = line[1]

        with exception_handler():
            secret_box.move(old_path, new_path)

    def do_mkdir(self, path):
        """
        mkdir <path>
        """
        if len(path) == 0:
            print "Usage: mkdir <path>"
            return

        with exception_handler():
            secret_box.mk_dir(path)

    def do_get(self, path):
        """
        get <filename>
        """
        if len(path) == 0:
            print "Usage: get <filename>"
            return

        with exception_handler():
            print secret_box.get(path)

    def do_put(self, line):
        """
        put <filename> <contents>
        """
        line = shlex.split(line)
        if len(line) < 2:
            print "Usage: put <filename> <contents>"
            return
        name = line[0]
        data = line[1]
        with exception_handler():
            secret_box.put(name, data)

    def do_del(self, path):
        """
        del <filename>
        """
        if len(path) == 0:
            print "Usage: del <filename>"
            return

        with exception_handler():
            secret_box.delete(path)

    def do_status(self, line):
        """
        Get the status of all providers
        """
        for i, provider in enumerate(providers):
            color = colorama.Fore.RESET
            if provider.status == ProviderStatus.GREEN:
                color = colorama.Fore.GREEN
            if provider.status == ProviderStatus.YELLOW:
                color = colorama.Fore.YELLOW
            if provider.status == ProviderStatus.RED:
                color = colorama.Fore.RED
            if provider.status == ProviderStatus.AUTH_FAIL:
                color = colorama.Fore.BLUE
            print color + str(i) + ":", str(provider)
        print colorama.Fore.RESET,

    def do_add(self, line):
        """
        add <provider type>
        provider_type can be one of "Dropbox", "Local", "Test", "TestServer"
        """
        provider = add_provider(line)
        if provider is None:
            return

        if provider.uuid in pp_providers():
            print provider.uuid, "exists!"
            return

        providers.append(provider)

        if secret_box.add_missing_provider(provider):
            print "Thanks for adding the missing provider! You should be out of read only mode."
            return

        print "Provider Added. Type 'reprovision' to begin using it!"

    def do_remove(self, line):
        """
        remove <provider index>
        Removes the provider at the specified index (view indices with 'status')
        """
        if len(providers) <= 3:
            print "You can never have under 3 providers!"
            return
        try:
            provider = providers.pop(int(line))
        except:
            print "Invalid index"
            return

        print "Removed provider", provider.uuid
        print "Type 'reprovision' to update system."

    def do_reprovision(self, line):
        """
        Reprovision the system to use a new provider set
        """
        with exception_handler():
            threshold = len(providers) - 1
            secret_box.reprovision(providers, threshold, threshold)

            print "Successfully reprovisioned"

    def do_set(self, line):
        """
        set <index> <property>
        Set the properties of a Test Provider at the index
        Property can be one of "active, offline, authfail, corrupt"
        """
        line = shlex.split(line.lower())
        index = line[0]
        prop = line[1]

        if len(line) < 2:
            print "Usage: set <index> <property>"
            return
        try:
            provider = providers[int(index)]
            assert provider.provider_name() == "Test"
        except AssertionError:
            print provider.uuid, "is not a Test Provider!"
            return
        except (ValueError, KeyError):
            print "Invalid index"
            return

        state = {"active": TestProviderState.ACTIVE,
                 "offline": TestProviderState.OFFLINE,
                 "authfail": TestProviderState.UNAUTHENTICATED,
                 "corrupt": TestProviderState.CORRUPTING}
        try:
            provider.set_state(state[prop])
        except KeyError:
            print "Invalid property"


if __name__ == '__main__':
    ConfigureLoop().cmdloop()
    MainLoop().cmdloop()
