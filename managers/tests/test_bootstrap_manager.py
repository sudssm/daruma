from managers.BootstrapManager import BootstrapManager, Bootstrap
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_filename

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]

key = generate_key()
name = generate_filename()
file_reconstruction_threshold = 2
bootstrap = Bootstrap(key, name, file_reconstruction_threshold)


def test_size():
    assert Bootstrap.SIZE == len(str(bootstrap))

def test_roundtrip():
    BM = BootstrapManager(providers, 2)
    BM.distribute_bootstrap(bootstrap)
    assert BM.recover_bootstrap() == bootstrap


def test_recover_nonexistent():
    for provider in providers:
        provider.wipe()
    BM = BootstrapManager(providers, 3)
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_multiple_sessions():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    BM = BootstrapManager(providers, 3)
    assert BM.recover_bootstrap() == bootstrap


def test_corrupt_recover():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[2].wipe()
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == bootstrap
        assert len(e.failures) == 2


def test_corrupt_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3
