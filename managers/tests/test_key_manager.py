from managers.KeyManager import KeyManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_filename

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]

key = generate_key()
name = generate_filename()


def test_roundtrip():
    KM = KeyManager(providers, 3)
    KM.distribute_key_and_name(key, name)
    assert KM.recover_key_and_name() == (key, name)


def test_recover_nonexistent():
    for provider in providers:
        provider.wipe()
    KM = KeyManager(providers, 3)
    try:
        KM.recover_key_and_name()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_multiple_sessions():
    KM = KeyManager(providers, 3)
    KM.distribute_key_and_name(key, name)

    KM = KeyManager(providers, 3)
    assert KM.recover_key_and_name() == (key, name)


def test_corrupt_recover():
    KM = KeyManager(providers, 3)
    KM.distribute_key_and_name(key, name)
    providers[0].wipe()
    providers[2].wipe()
    try:
        KM.recover_key_and_name()
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == (key, name)
        assert len(e.failures) == 2


def test_corrupt_fail():
    KM = KeyManager(providers, 3)
    KM.distribute_key_and_name(key, name)
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    try:
        KM.recover_key_and_name()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3
