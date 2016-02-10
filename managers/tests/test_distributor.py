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


def test_small_mutate_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[0], "test", 1)

    try:
        print FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 1
        assert e.failures[0].provider == providers[0]


def test_medium_mutate_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[0], "test", 10)

    try:
        print FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 1
        assert e.failures[0].provider == providers[0]


def test_big_mutate_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[0], "test", 20)

    print [provider.get("test") for provider in providers]

    try:
        print FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 1
        assert e.failures[0].provider == providers[0]


def test_mutate_two_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")

    mutate(providers[2], "test", 20)
    mutate(providers[3], "test", 20)

    try:
        FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert sorted([f.provider for f in e.failures]) == sorted([providers[2], providers[3]])


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
