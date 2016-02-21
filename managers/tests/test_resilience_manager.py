from driver.SecretBox import SecretBox
from custom_exceptions import exceptions
from providers.TestProvider import TestProvider, TestProviderState
import pytest


providers = [TestProvider("tmp/" + str(i)) for i in xrange(5)]


def setup_function(function):
    for provider in providers:
        provider.set_state(TestProviderState.ACTIVE)


def test_failing():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.FAILING, 3)
    # try getting, ensure that we caught the errors
    assert SB.get("test") == "data"
    # one for load manifest, one for get file
    assert providers[0].errors == 2
    providers[0].set_state(TestProviderState.ACTIVE)
    # check that everything is fixed - we should get no more errors
    assert SB.get("test") == "data"
    assert providers[0].errors == 2


def test_permanently_offline_get():
    SB = SecretBox.provision(providers, 3, 3)
    SB.put("test", "data")
    providers[0].set_state(TestProviderState.OFFLINE)
    # TODO i should be able to still get this somehow?
    with pytest.raises(exceptions.RedProviderFailure):
        SB.get("test")


def test_permanently_offline_load():
    print providers[0].state
    SecretBox.provision(providers, 3, 3)
    providers[0].set_state(TestProviderState.OFFLINE)
    with pytest.raises(exceptions.RedProviderFailure):
        SecretBox.load(providers)
