from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
import pytest

cm = CredentialManager()
cm.load()

providers = [LocalFilesystemProvider(cm, "tmp/" + str(i)) for i in xrange(5)]


def teardown_function(function):
    cm.clear_user_credentials()


def test_init():
    SB = SecretBox.provision(providers, 3, 3)
    assert len(SB.ls("")) == 0


def test_roundtrip():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    assert SB.ls("") == [{"name": "test", "is_directory": False, "size": 4}]
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
    assert sorted(SB.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]

    SecretBox.load(providers)
    assert sorted(SB.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]
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
    bootstrap_reconstruction_threshold = 3
    file_reconstruction_threshold = 2
    SB = SecretBox.provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)

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


def test_add_provider():
    SB = SecretBox.provision(providers[0:4], 3, 3)
    SB.put("test", "data")
    SB.reprovision(providers, 4, 4)

    assert SB.get("test") == "data"
    # check that we can bootstrap
    SB = SecretBox.load(providers)

    # check that k has been changed
    providers[0].wipe()
    providers[1].wipe()

    with pytest.raises(exceptions.FatalOperationFailure):
        SB.get("test")


def test_remove_provider():
    SB = SecretBox.provision(providers, 4, 4)
    SB.put("test", "data")

    SB.reprovision(providers[0:4], 3, 3)

    assert SB.get("test") == "data"

    # check that we can bootstrap
    SB = SecretBox.load(providers[0:4])
    assert SB.get("test") == "data"

    # check that k has been changed
    providers[0].wipe()

    assert SB.get("test") == "data"


def test_read_only_mode():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "file")

    SB = SecretBox.load(providers[0:3])
    with pytest.raises(exceptions.ReadOnlyMode):
        SB.put("test", "something else")

    assert SB.get_missing_providers() == map(lambda provider: provider.uuid, providers[3:])

    # check that we can still read
    assert SB.get("test") == "file"


def test_read_only_mode_fix_by_adding():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("file", "data")

    SB = SecretBox.load(providers[:3])

    with pytest.raises(exceptions.ReadOnlyMode):
        SB.put("test", "file")

    missing_providers = providers[3:]
    assert SB.get_missing_providers() == map(lambda provider: provider.uuid, missing_providers)

    # try an invalid add_missing_provider call
    assert SB.add_missing_provider(providers[0]) is False

    # add one missing provider
    assert SB.add_missing_provider(missing_providers.pop())
    assert SB.get_missing_providers() == map(lambda provider: provider.uuid, missing_providers)

    # make sure we can still get
    assert SB.get("file") == "data"

    # but that we can't read
    with pytest.raises(exceptions.ReadOnlyMode):
        SB.put("test", "file")

    # add the other missing provider
    assert SB.add_missing_provider(missing_providers.pop())
    assert SB.get_missing_providers() == []

    # check that we are out of read only mode
    SB.put("test", "file")
    assert SB.get("test") == "file"


def test_read_only_mode_fix_by_removing():
    SecretBox.provision(providers, 3, 3)

    provider_subset = providers[0:3]

    SB = SecretBox.load(provider_subset)

    with pytest.raises(exceptions.ReadOnlyMode):
        SB.put("test", "file")

    SB.reprovision(provider_subset, 2, 2)

    # check that we are out of read only mode
    SB.put("test", "file")
    assert SB.get("test") == "file"


def test_reprovision_new_set():
    SB = SecretBox.provision(providers[:3], 2, 2)
    SB.put("test", "file")

    SB.reprovision(providers[2:], 2, 2)
    assert SB.get("test") == "file"


def test_provision_bad_threshold():
    with pytest.raises(ValueError):
        SecretBox.provision(providers, 5, 5)


def test_reprovision_bad_threshold():
    SB = SecretBox.provision(providers[:3], 2, 2)
    with pytest.raises(ValueError):
        SB.reprovision(providers[3:], 2, 2)
