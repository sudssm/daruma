from managers.Distributor import FileDistributor
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from crypto.encryption import generate_key
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]

def test_get_nonexisting():
    for provider in providers:
        provider.wipe()

    FD = FileDistributor(providers, 3)
    with pytest.raises(exceptions.FileNotFound):
        FD.get("test", "dummy")

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
    with pytest.raises(exceptions.FileNotFound):
        FD.get("test", key)

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
    assert FD.get("test", key) == "data"

def test_corrupt_fail():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    with pytest.raises(exceptions.DecodeError):
        FD.get("test", key)

def test_wrong_key():
    wrong_key = generate_key()
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    with pytest.raises(exceptions.DecryptError):
     FD.get("test", wrong_key)

def test_multiple_sessions():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    FD = FileDistributor(providers, 3)
    assert FD.get("test", key) == "data"