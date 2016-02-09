from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]


def test_init():
    SB = SecretBox.provision(providers, 3, 3)
    assert len(SB.ls()) == 0


def test_roundtrip():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    assert SB.ls() == ["test"]
    assert SB.get("test") == "data"


def test_get_nonexistent():
    SB = SecretBox.provision(providers, 3, 3)
    with pytest.raises(exceptions.FileNotFound):
        SB.get("blah")


def test_delete():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    SB.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        SB.get("test")


def test_update():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    SB.put("test", "newdata")
    assert SB.get("test") == "newdata"


def test_multiple_sessions():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    SB.put("test2", "moredata")
    assert sorted(SB.ls()) == ["test", "test2"]

    SecretBox.load(providers)
    assert sorted(SB.ls()) == ["test", "test2"]
    assert SB.get("test") == "data"
    assert SB.get("test2") == "moredata"


def test_corrupt_recover():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    SecretBox.load(providers)
    assert SB.get("test") == "data"


def test_corrupt_fail():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    with pytest.raises(exceptions.FatalOperationFailure):
        SecretBox.load(providers)


def test_different_ks():
    SB = SecretBox.provision(providers, 2, 3)
    SB.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    # should be able to recover the key, but not files
    SB = SecretBox.load(providers)
    try:
        SB.ls()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3


def test_different_ks_2():
    SB = SecretBox.provision(providers, 3, 2)
    SB.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()

    # should be able to recover the key
    SB = SecretBox.load(providers)

    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    # but now can't recover the key
    with pytest.raises(Exception):
        SecretBox.load(providers, 3, 2)

    # should still be able to recover the files
    # even though 3rd provider went down after initializing
    assert SB.get("test") == "data"
