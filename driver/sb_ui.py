"""
super ugly hacked together thing to play with secretbox
usage:
    python sb_ui.py init n k_key k_file tmp_dir
    python sb_ui.py start n tmp_dir

arg 1 is init if you want to start a new secretbox from scratch
         start if you want to resume an existing secretbox

n is the number of local providers to make
Script will always create a test Dropbox Provider
k_key/k_file is the number of providers that need to be up to recover key/file
tmp_dir is a local directory that will act as the providers
"""
import shlex

from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from providers.DropboxProvider import DropboxProvider
from providers.ProviderManager import ProviderManager
from providers.CredentialManager import CredentialManager
import sys

cm = CredentialManager()
cm.load()
pm = ProviderManager(cm)

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


providers = [LocalFilesystemProvider(tmp_dir + "/" + str(i)) for i in xrange(n)]

# attempt to load an authenticated dropbox provider
dropbox_provider = pm.load_dropbox_provider()
if dropbox_provider is None:
    # start a dropbox provider
    print "Visit", pm.start_dropbox_connection(), "to sign in to Dropbox"
    localhost_url = raw_input("Enter resulting url (starts with localhost): ")
    dropbox_provider = pm.finish_dropbox_connection(localhost_url)
providers.append(dropbox_provider)

if cmd == "init":
    SB = SecretBox.provision(providers, k_key, k_file)
else:
    SB = SecretBox.load(providers)

while True:
    print "\n"
    print "ls, get, put, del, exit"
    cmd = shlex.split(raw_input("> "))

    if cmd[0] == "ls":
        files = SB.ls()
        if len(files) == 0:
            print "EMPTY"
        for item in files:
            print "-", item
    if cmd[0] == "get":
        if len(cmd) < 2:
            print "Usage: get <filename>"
            continue
        name = cmd[1]
        try:
            print SB.get(name)
        except exceptions.FileNotFound:
            print "File does not exist!"
    if cmd[0] == "put":
        if len(cmd) < 3:
            print "Usage: put <filename> <contents>"
            continue
        name = cmd[1]
        data = cmd[2]
        SB.put(name, data)
    if cmd[0] == "del":
        if len(cmd) < 2:
            print "Usage: del <filename>"
            continue
        name = cmd[1]
        try:
            SB.delete(name)
        except exceptions.FileNotFound:
            print "File does not exist!"
    if cmd[0] == "exit":
        break
