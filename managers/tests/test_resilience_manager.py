from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.TestProvider import TestProvider, TestProviderState
from providers.BaseProvider import ProviderStatus
import pytest


providers = [TestProvider("tmp/" + str(i)) for i in xrange(5)]


def setup_function(function):
    for provider in providers:
        provider.set_state(TestProviderState.ACTIVE)
        provider.errors = 0


def test_repair_file():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.FAILING)

    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.RED

    providers[0].set_state(TestProviderState.ACTIVE)

    # check that repairs happen properly
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW

    # check that the 0th provider is now fully operational
    providers[3].set_state(TestProviderState.OFFLINE)
    providers[4].set_state(TestProviderState.OFFLINE)
    assert SB.get("test") == "data"


def test_return_to_yellow():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")

    providers[0].set_state(TestProviderState.OFFLINE)
    providers[1].set_state(TestProviderState.OFFLINE)

    SB.ls()

    assert providers[0].status == ProviderStatus.RED
    assert providers[1].status == ProviderStatus.RED

    providers[0].set_state(TestProviderState.ACTIVE)
    providers[1].set_state(TestProviderState.ACTIVE)

    SB.ls()

    assert providers[0].status == ProviderStatus.YELLOW
    assert providers[1].status == ProviderStatus.YELLOW


def test_wiped_provider():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")

    providers[0].wipe()

    # check that repairs happen properly
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW

    # check that the 0th provider is now fully operational
    providers[3].set_state(TestProviderState.OFFLINE)
    providers[4].set_state(TestProviderState.OFFLINE)
    assert SB.get("test") == "data"


def test_temporary_offline_put():
    SB = SecretBox.provision(providers, 3, 3)
    # failing for 5 turns
    providers[0].set_state(TestProviderState.FAILING, 5)
    SB.put("test", "data")

    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW


def test_offline_provision():
    providers[0].set_state(TestProviderState.FAILING, 4)
    with pytest.raises(exceptions.ProviderFailure):
        SecretBox.provision(providers, 3, 3)


def test_temporary_offline_load():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.FAILING, 4)
    SB = SecretBox.load(providers)
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW


def test_permanently_offline_get():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.OFFLINE)
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.RED


def test_permanently_offline_load():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.OFFLINE)
    SB = SecretBox.load(providers)
    assert providers[0].status == ProviderStatus.RED
    assert SB.get("test") == "data"


def test_permanently_offline_put():
    SB = SecretBox.provision(providers, 3, 3)
    providers[0].set_state(TestProviderState.OFFLINE)
    with pytest.raises(exceptions.FatalOperationFailure):
        SB.put("test", "data")
    assert providers[0].status == ProviderStatus.RED


def test_permanently_authfail_get():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.UNAUTHENTICATED)
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.AUTH_FAIL


def test_corrupting():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.CORRUPTING)
    assert SB.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW
