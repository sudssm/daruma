from managers.KeyManager import KeyManager
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]


def test_roundtrip():
    KM = KeyManager(providers, 3)
    key = KM.distribute_new_key()
    assert KM.recover_key() == key


def test_recover_nonexistent():
    for provider in providers:
        provider.wipe()
    KM = KeyManager(providers, 3)
    # TODO should be a better error
    with pytest.raises(Exception):
        KM.recover_key()


def test_multiple_sessions():
    KM = KeyManager(providers, 3)
    key = KM.distribute_new_key()

    KM = KeyManager(providers, 3)
    assert KM.recover_key() == key


def test_corrupt_recover():
    KM = KeyManager(providers, 3)
    key = KM.distribute_new_key()
    providers[0].wipe()
    providers[2].wipe()
    assert KM.recover_key() == key


def test_corrupt_fail():
    KM = KeyManager(providers, 3)
    KM.distribute_new_key()
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    with pytest.raises(exceptions.KeyReconstructionError):
        KM.recover_key()
