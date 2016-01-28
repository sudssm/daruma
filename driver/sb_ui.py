"""
super ugly hacked together thing to play with secretbox
usage:
    python sb_ui.py (init | start | help) n k_key k_file tmp_dir

arg 1 is init if you want to start a new secretbox from scratch
         start if you want to resume an existing secretbox

n is the number of local providers to make
k_key/k_file is the number of providers that need to be up to recover key/file
tmp_dir is a local directory that will act as the providers
"""
import shlex


from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
import sys

try:
    cmd = sys.argv[1]
    n = int(sys.argv[2])
    k_key = int(sys.argv[3])
    k_file = int(sys.argv[4])
    tmp_dir = sys.argv[5]

    if cmd not in ["init", "start"]:
        raise Exception
except:
    print __doc__
    sys.exit()


providers = [LocalFilesystemProvider(tmp_dir + "/" + str(i)) for i in xrange(n)]
SB = SecretBox(providers, k_key, k_file)
if cmd == "init":
    SB.provision()
else:
    SB.start()

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
