from managers.Distributor import FileDistributor
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]


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
