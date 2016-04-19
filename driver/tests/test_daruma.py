from driver.Daruma import Daruma
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
import pytest

cm = CredentialManager()
cm.load()


def make_local(cm, path):
    provider = LocalFilesystemProvider(cm)
    provider.connect(path)
    return provider

providers = [make_local(cm, "tmp/" + str(i)) for i in xrange(5)]


def teardown_function(function):
    cm.clear_user_credentials()


def test_init():
    daruma = Daruma.provision(providers, 3, 3)
    assert len(daruma.ls("")) == 0


def test_roundtrip():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    assert daruma.ls("") == [{"name": "test", "is_directory": False, "size": 4}]
    assert daruma.get("test") == "data"


def test_get_nonexistent():
    daruma = Daruma.provision(providers, 3, 3)
    with pytest.raises(exceptions.FileNotFound):
        daruma.get("blah")


def test_delete():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    daruma.delete("test")
    with pytest.raises(exceptions.FileNotFound):
        daruma.get("test")


def test_update():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    daruma.put("test", "newdata")
    assert daruma.get("test") == "newdata"


def test_multiple_sessions():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    daruma.put("test2", "moredata")
    assert sorted(daruma.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]

    daruma, _ = Daruma.load(providers)
    assert sorted(daruma.ls("")) == [{"name": "test", "is_directory": False, "size": 4}, {"name": "test2", "is_directory": False, "size": 8}]
    assert daruma.get("test") == "data"
    assert daruma.get("test2") == "moredata"


def test_corrupt_recover():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()

    Daruma.load(providers)
    assert daruma.get("test") == "data"


def test_corrupt_fail():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    with pytest.raises(exceptions.FatalOperationFailure):
        Daruma.load(providers)


def test_different_ks():
    bootstrap_reconstruction_threshold = 3
    file_reconstruction_threshold = 2
    daruma = Daruma.provision(providers, bootstrap_reconstruction_threshold, file_reconstruction_threshold)

    daruma.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()

    # should be able to recover the key
    daruma, _ = Daruma.load(providers)

    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()

    # but now can't recover the key
    with pytest.raises(Exception):
        Daruma.load(providers, 3, 2)

    # should still be able to recover the files
    # even though 3rd provider went down after initializing
    assert daruma.get("test") == "data"


def test_add_provider():
    daruma = Daruma.provision(providers[0:4], 3, 3)
    daruma.put("test", "data")
    daruma.reprovision(providers, 4, 4)

    assert daruma.get("test") == "data"
    # check that we can bootstrap
    daruma, _ = Daruma.load(providers)

    # check that k has been changed
    providers[0].wipe()
    providers[1].wipe()

    with pytest.raises(exceptions.FatalOperationFailure):
        daruma.get("test")


def test_remove_provider():
    daruma = Daruma.provision(providers, 4, 4)
    daruma.put("test", "data")

    daruma.reprovision(providers[0:4], 3, 3)

    assert daruma.get("test") == "data"

    # check that we can bootstrap
    daruma, _ = Daruma.load(providers[0:4])
    assert daruma.get("test") == "data"

    # check that k has been changed
    providers[0].wipe()

    assert daruma.get("test") == "data"


def test_read_only_mode():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "file")

    daruma, _ = Daruma.load(providers[0:3])
    with pytest.raises(exceptions.ReadOnlyMode):
        daruma.put("test", "something else")

    assert daruma.get_missing_providers() == map(lambda provider: provider.uuid, providers[3:])

    # check that we can still read
    assert daruma.get("test") == "file"


def test_read_only_mode_fix_by_adding():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("file", "data")

    daruma, _ = Daruma.load(providers[:3])

    with pytest.raises(exceptions.ReadOnlyMode):
        daruma.put("test", "file")

    missing_providers = providers[3:]
    assert daruma.get_missing_providers() == map(lambda provider: provider.uuid, missing_providers)

    # try an invalid add_missing_provider call
    assert daruma.add_missing_provider(providers[0]) is False

    # add one missing provider
    assert daruma.add_missing_provider(missing_providers.pop())
    assert daruma.get_missing_providers() == map(lambda provider: provider.uuid, missing_providers)

    # make sure we can still get
    assert daruma.get("file") == "data"

    # but that we can't read
    with pytest.raises(exceptions.ReadOnlyMode):
        daruma.put("test", "file")

    # add the other missing provider
    assert daruma.add_missing_provider(missing_providers.pop())
    assert daruma.get_missing_providers() == []

    # check that we are out of read only mode
    daruma.put("test", "file")
    assert daruma.get("test") == "file"


def test_read_only_mode_fix_by_removing():
    Daruma.provision(providers, 3, 3)

    provider_subset = providers[0:3]

    daruma, _ = Daruma.load(provider_subset)

    with pytest.raises(exceptions.ReadOnlyMode):
        daruma.put("test", "file")

    daruma.reprovision(provider_subset, 2, 2)

    # check that we are out of read only mode
    daruma.put("test", "file")
    assert daruma.get("test") == "file"


def test_reprovision_new_set():
    daruma = Daruma.provision(providers[:3], 2, 2)
    daruma.put("test", "file")

    daruma.reprovision(providers[2:], 2, 2)
    assert daruma.get("test") == "file"


def test_provision_bad_threshold():
    with pytest.raises(ValueError):
        Daruma.provision(providers, 5, 5)


def test_reprovision_bad_threshold():
    daruma = Daruma.provision(providers[:3], 2, 2)
    with pytest.raises(ValueError):
        daruma.reprovision(providers[3:], 2, 2)


def test_extra_providers():
    Daruma.provision(providers, 4, 4)
    daruma, extra_providers = Daruma.load(providers)
    assert extra_providers == []
    Daruma.provision(providers[:3], 2, 2)
    daruma, extra_providers = Daruma.load(providers)
    assert daruma.file_manager.providers == providers[:3]
    assert sorted(extra_providers) == sorted(providers[3:])
