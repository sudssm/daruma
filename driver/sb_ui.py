"""
super ugly hacked together thing to play with secretbox
usage:
    python sb_ui.py init n k_key k_file tmp_dir
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
from providers.BaseProvider import ProviderStatus
import sys
import colorama

colorama.init()
try:
    cmd = sys.argv[1]
    n = int(sys.argv[2])

    if cmd == "init":
        k_key = int(sys.argv[3])
        k_file = int(sys.argv[4])
        tmp_dir = sys.argv[5]
    elif cmd == "start":
        tmp_dir = sys.argv[3]
    else:
        raise Exception
except:
    print __doc__
    sys.exit()


providers = [TestProvider(tmp_dir + "/" + str(i)) for i in xrange(n)]
if cmd == "init":
    SB = SecretBox.provision(providers, k_key, k_file)
else:
    SB = SecretBox.load(providers)

while True:
    print "\n"
    print "ls, get, put, del, set, status, exit"
    cmd = shlex.split(raw_input("> "))

    if len(cmd) == 0:
        continue

    if cmd[0] == "ls":
        try:
            files = SB.ls()
            if len(files) == 0:
                print "EMPTY"
            for item in files:
                print "-", item
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except Exception as e:
            print traceback.format_exc()
    if cmd[0] == "get":
        if len(cmd) < 2:
            print "Usage: get <filename>"
            continue
        name = cmd[1]
        try:
            print SB.get(name)
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except exceptions.FileNotFound:
            print "File does not exist!"
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except Exception as e:
            print traceback.format_exc()
    if cmd[0] == "put":
        if len(cmd) < 3:
            print "Usage: put <filename> <contents>"
            continue
        name = cmd[1]
        data = cmd[2]
        try:
            SB.put(name, data)
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except Exception as e:
            print traceback.format_exc()
    if cmd[0] == "del":
        if len(cmd) < 2:
            print "Usage: del <filename>"
            continue
        name = cmd[1]
        try:
            SB.delete(name)
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except exceptions.FileNotFound:
            print "File does not exist!"
        except exceptions.FatalOperationFailure:
            print "Operation Failed! check status"
        except Exception as e:
            print traceback.format_exc()
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
    if cmd[0] == "exit":
        break
