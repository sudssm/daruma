"""
super ugly hacked together thing to play with secretbox
usage:
    python sb_ui.py init n tmp_dir
    python sb_ui.py start n tmp_dir

arg 1 is init if you want to start a new secretbox from scratch
         start if you want to resume an existing secretbox

n is the number of local providers to make
k_key/k_file is the number of providers that need to be up to recover key/file
tmp_dir is a local directory that will act as the providers
"""
import shlex
import traceback
from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.TestProvider import TestProvider, TestProviderState
from providers.DropboxProvider import DropboxProvider
from providers.BaseProvider import ProviderStatus
from managers.CredentialManager import CredentialManager
from contextlib import contextmanager
import sys
import colorama


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
    except EOFError:
        sys.exit()
    except:
        print traceback.format_exc()

credential_manager = CredentialManager()
credential_manager.load()
colorama.init()

try:
    cmd = sys.argv[1]
    n = int(sys.argv[2])
    tmp_dir = sys.argv[3]

    if cmd not in ["init", "start"]:
        raise Exception
except:
    print __doc__
    sys.exit()


providers = [TestProvider(credential_manager, tmp_dir + "/" + str(i)) for i in xrange(n)]
# attempt to load authenticated dropbox providers
dropbox_providers, failed_emails = DropboxProvider.load_cached_providers(credential_manager)

if len(failed_emails) > 0:
    print "Failed to load DropboxProviders:", failed_emails

if len(dropbox_providers) == 0:
    # start a dropbox provider
    dropbox_provider = DropboxProvider(credential_manager)
    print "Visit", dropbox_provider.start_connection(), "to sign in to Dropbox"
    localhost_url = raw_input("Enter resulting url (starts with localhost): ")
    dropbox_provider.finish_connection(localhost_url)
    providers.append(dropbox_provider)
else:
    print "Loaded Dropbox accounts:", [dbp.id for dbp in dropbox_providers]
    providers += dropbox_providers

if cmd == "init":
    SB = SecretBox.provision(providers, n-1, n-1)
else:
    SB = SecretBox.load(providers)

while True:
    print "\n"
    print "SB commands: ls, mv, mkdir, get, put, del, exit"
    print "provider commands: add, remove, set, wipe, status"

    with exception_handler():
        cmd = shlex.split(raw_input("> "))

    if len(cmd) == 0:
        continue

    if cmd[0] == "ls":
        if len(cmd) > 1:
            target = cmd[1]
        else:
            target = ""

        with exception_handler():
            files = SB.ls(target)

            if len(files) == 0:
                print "EMPTY"
            for item in files:
                is_dir = item['is_directory']
                print "DIR" if is_dir else "" + str(item['size']),
                print "\t" + item['name']

    if cmd[0] == "mv":
        if len(cmd) < 3:
            print "Usage: mv <old_path> <new_path>"
            continue
        old_path = cmd[1]
        new_path = cmd[2]

        with exception_handler():
            SB.move(old_path, new_path)

    if cmd[0] == "mkdir":
        if len(cmd) < 2:
            print "Usage: mkdir <path>"
            continue
        path = cmd[1]

        with exception_handler():
            SB.mk_dir(path)

    if cmd[0] == "get":
        if len(cmd) < 2:
            print "Usage: get <filename>"
            continue
        name = cmd[1]

        with exception_handler():
            print SB.get(name)

    if cmd[0] == "put":
        if len(cmd) < 3:
            print "Usage: put <filename> <contents>"
            continue
        name = cmd[1]
        data = cmd[2]
        with exception_handler():
            SB.put(name, data)

    if cmd[0] == "del":
        if len(cmd) < 2:
            print "Usage: del <filename>"
            continue
        name = cmd[1]

        with exception_handler():
            SB.delete(name)

    if cmd[0] == "set":
        if len(cmd) < 3:
            print "Usage: set <all, n> <active, offline, authfail, corrupt>"
            continue

        try:
            if cmd[1] == "all":
                n = len(providers)
            else:
                n = int(cmd[1])
            assert 0 < n
            assert n <= len(providers)
            assert cmd[2] in ["active", "offline", "authfail", "corrupt"]
        except (AssertionError, ValueError):
            print "Invalid input"
            print "Usage: set <all, n> <active, offline, authfail, corrupt>"
        for provider in providers[0:n]:
            if cmd[2] == "active":
                provider.set_state(TestProviderState.ACTIVE)
            if cmd[2] == "offline":
                provider.set_state(TestProviderState.OFFLINE)
            if cmd[2] == "authfail":
                provider.set_state(TestProviderState.UNAUTHENTICATED)
            if cmd[2] == "corrupt":
                provider.set_state(TestProviderState.CORRUPTING)

    if cmd[0] == "status":
        for provider in providers:
            color = colorama.Fore.RESET
            if provider.status == ProviderStatus.GREEN:
                color = colorama.Fore.GREEN
            if provider.status == ProviderStatus.YELLOW:
                color = colorama.Fore.YELLOW
            if provider.status == ProviderStatus.RED:
                color = colorama.Fore.RED
            if provider.status == ProviderStatus.AUTH_FAIL:
                color = colorama.Fore.BLUE
            print color + str(provider)
        print colorama.Fore.RESET,

    if cmd[0] == "wipe":
        if len(cmd) < 2:
            print "Usage: wipe <provider #>"
            continue
        try:
            n = int(cmd[1])
            assert 0 <= n
            assert n < len(providers)
        except (AssertionError, ValueError):
            print "Invalid input"
            print "Usage: wipe <provider #>"
        providers[n].wipe()

    if cmd[0] == "add":
        with exception_handler():
            providers.append(TestProvider(tmp_dir + "/" + str(len(providers))))
            SB.add_provider(providers[-1])

    if cmd[0] == "remove":
        with exception_handler():
            provider = providers.pop(-1)
            SB.remove_provider(provider)

    if cmd[0] == "exit":
        break
