from driver.Daruma import Daruma
from custom_exceptions import exceptions
from managers.CredentialManager import CredentialManager
from providers.TestProvider import TestProvider, TestProviderState
from providers.BaseProvider import ProviderStatus
import pytest


cm = CredentialManager()
cm.load()


def make_local(cm, path):
    provider = TestProvider(cm)
    provider.connect(path)
    return provider

providers = [make_local(cm, "tmp/" + str(i)) for i in xrange(5)]


def teardown_function(function):
    cm.clear_user_credentials()


def setup_function(function):
    for provider in providers:
        provider.set_state(TestProviderState.ACTIVE)
        provider.errors = 0


def test_repair_file():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.FAILING)

    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.RED

    providers[0].set_state(TestProviderState.ACTIVE)

    # check that repairs happen properly
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW

    # check that the 0th provider is now fully operational
    providers[3].set_state(TestProviderState.OFFLINE)
    providers[4].set_state(TestProviderState.OFFLINE)
    assert daruma.get("test") == "data"


def test_return_to_yellow():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")

    providers[0].set_state(TestProviderState.OFFLINE)
    providers[1].set_state(TestProviderState.OFFLINE)

    daruma.get("test")

    assert providers[0].status == ProviderStatus.RED
    assert providers[1].status == ProviderStatus.RED

    providers[0].set_state(TestProviderState.ACTIVE)
    providers[1].set_state(TestProviderState.ACTIVE)

    daruma.get("test")

    assert providers[0].status == ProviderStatus.YELLOW
    assert providers[1].status == ProviderStatus.YELLOW


def test_wiped_provider():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")

    providers[0].wipe()

    # check that repairs happen properly
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW

    # check that the 0th provider is now fully operational
    providers[3].set_state(TestProviderState.OFFLINE)
    providers[4].set_state(TestProviderState.OFFLINE)
    assert daruma.get("test") == "data"


def test_temporary_offline_put():
    daruma = Daruma.provision(providers, 3, 3)
    # failing for 2 turns
    providers[0].set_state(TestProviderState.FAILING, 2)
    daruma.put("test", "data")

    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW


def test_offline_provision():
    providers[0].set_state(TestProviderState.FAILING, 4)
    with pytest.raises(exceptions.FatalOperationFailure) as excinfo:
        Daruma.provision(providers, 3, 3)
    failures = excinfo.value.failures
    assert len(failures) == 1
    assert failures[0].provider == providers[0]


def test_temporary_offline_load():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.FAILING, 4)
    daruma, _ = Daruma.load(providers)
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW


def test_permanently_offline_get():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.OFFLINE)
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.RED


def test_permanently_offline_load():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.OFFLINE)
    daruma, _ = Daruma.load(providers)
    assert providers[0].status == ProviderStatus.RED
    assert daruma.get("test") == "data"


def test_permanently_offline_put():
    daruma = Daruma.provision(providers, 3, 3)
    providers[0].set_state(TestProviderState.OFFLINE)
    with pytest.raises(exceptions.FatalOperationFailure):
        daruma.put("test", "data")
    assert providers[0].status == ProviderStatus.RED


def test_permanently_authfail_get():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.UNAUTHENTICATED)
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.AUTH_FAIL


def test_corrupting():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")
    providers[0].set_state(TestProviderState.CORRUPTING)
    assert daruma.get("test") == "data"
    assert providers[0].status == ProviderStatus.YELLOW


def test_attempt_repair_in_read_only():
    daruma = Daruma.provision(providers, 3, 3)
    daruma.put("test", "data")

    # load with only 4 providers, one of which is bad
    providers[0].set_state(TestProviderState.OFFLINE)
    daruma, _ = Daruma.load(providers[:4])

    assert daruma.get("test") == "data"
