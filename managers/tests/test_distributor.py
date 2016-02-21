from managers.Distributor import FileDistributor
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from struct import pack
from random import randint
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]


def setup_function(function):
    for provider in providers:
        provider.wipe()


def test_get_nonexisting():
    for provider in providers:
        provider.wipe()

    FD = FileDistributor(providers, 3)
    try:
        FD.get("test", "dummy")
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_roundtrip():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    key2 = FD.put("another", "data2")
    assert FD.get("test", key) == "data"
    assert FD.get("another", key2) == "data2"


def test_roundtrip_with_key():
    key = generate_key()
    FD = FileDistributor(providers, 3)
    FD.put("test", "data", key)
    assert FD.get("test", key) == "data"


def test_delete():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    FD.delete("test")
    try:
        FD.get("test", key)
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_update():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    key = FD.put("test", "other")
    assert FD.get("test", key) == "other"


def test_corrupt_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()
    try:
        FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 2


def test_corrupt_fail():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    try:
        FD.get("test", key)
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3


def mutate(provider, filename, mutations):
    share = list(provider.get(filename))
    for i in xrange(mutations):
        corrupt = pack("h", randint(0, 255))
        location = randint(0, (len(share)-2) / 2) * 2
        share[location] = corrupt[0]
        share[location + 1] = corrupt[1]
    provider.put(filename, "".join(share))


def test_mutate_recover():
    # the first share is bad!
    shares = ['\x04\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\r\x02\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x05(\xd8\xea\x9bo\xed\xc5\x13\xab\xa4\xc8\xebO\x8b', '\x01\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\r\x02\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00}\xcb\x9e\xb2*\xb4\xea?1\xa3)H[?\xb9', '\xd0\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\xc8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x14\x00\x00\x00\x00\x00}\x00;\x00\x00\x00\x00\x00\x00\x00\xe6\x00\xb8\x00\x90\x00\r\x02\x00\xcc^\x0c\x0b\x02\xe4\x00\x00\x00U\x00\x1c\x00\xb6\x00\x93\x00\x00\x00\x00\x00\x89\xbf\xc6D\xfe\xc5\x0fh^\xc5\x1d\x00\xef\x00\xe4', '\x03\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\r\x02\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00gs\x9e\n\x9f\x8f&\xaa\xad,\xc5G\x9a=]', '\x02\x00\x00\x00\x0f\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04\x00\r\x02\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x93\x07\xc6\xfcK\xfe\xc3\xfd\xc2J\xa0B,\x0f\x00']
    tmp = shares[2]
    shares[2] = shares[0]
    shares[0] = tmp
    key = "%\xae\xbc\x15\t)\xb7\x19\x89\xe4^\xdd\xda>[J\xb1\xaag\x8f\x94\x9b\xe3\xad\xd8*{D\xf8.\xb4\xdf"
    for share, provider in zip(shares, providers):
        provider.put("test", share)

    FD = FileDistributor(providers, 3)
    #FD.put("test", "data", key)
    #mutate(providers[0], "test", 20)
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FD.get("test", key)
    assert excinfo.value.result == "data"
    assert len(excinfo.value.failures) == 1
    print excinfo.value.failures[0].provider.provider_path
    print providers[0].provider_path
    assert excinfo.value.failures[0].provider == providers[0]
    assert False


def test_mutate_two_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[2], "test", 20)
    mutate(providers[3], "test", 20)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FD.get("test", key)
    assert excinfo.value.result == "data"
    assert sorted([f.provider for f in excinfo.value.failures]) == sorted([providers[2], providers[3]])


def test_mutate_fail():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[1], "test", 20)
    mutate(providers[2], "test", 20)
    mutate(providers[3], "test", 20)

    with pytest.raises(exceptions.FatalOperationFailure):
        FD.get("test", key)


def test_wrong_key():
    wrong_key = generate_key()
    FD = FileDistributor(providers, 3)
    FD.put("test", "data")
    with pytest.raises(exceptions.FatalOperationFailure):
        FD.get("test", wrong_key)


def test_multiple_sessions():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    FD = FileDistributor(providers, 3)
    assert FD.get("test", key) == "data"
