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
    assert FD.get("test", "dummy")[0] is None


def test_roundtrip():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    (key2, failed_providers_map) = FD.put("another", "data2")
    assert FD.get("test", key)[0] == "data"
    assert FD.get("another", key2)[0] == "data2"


def test_roundtrip_with_key():
    key = generate_key()
    FD = FileDistributor(providers, 3)
    FD.put("test", "data", key)
    assert FD.get("test", key)[0] == "data"


def test_delete():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    FD.delete("test")
    assert FD.get("test", key)[0] is None


def test_update():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    (key, failed_providers_map) = FD.put("test", "other")
    assert FD.get("test", key)[0] == "other"


def test_corrupt_recover():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()
    assert FD.get("test", key)[0] == "data"


def test_corrupt_fail():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    assert FD.get("test", key)[0] is None


def test_wrong_key():
    wrong_key = generate_key()
    FD = FileDistributor(providers, 3)
    data, _ = FD.put("test", "data")
    # TODO something different should happen here eventually
    with pytest.raises(exceptions.DecryptError):
        FD.get("test", wrong_key)


def test_multiple_sessions():
    FD = FileDistributor(providers, 3)
    (key, failed_providers_map) = FD.put("test", "data")
    FD = FileDistributor(providers, 3)
    assert FD.get("test", key)[0] == "data"
