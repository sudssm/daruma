from managers.BootstrapManager import BootstrapManager, Bootstrap
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
from tools.encryption import generate_key
from tools.utils import generate_random_name
import pytest

cm = CredentialManager()
cm.load()

providers = [LocalFilesystemProvider(cm, "tmp/" + str(i)) for i in xrange(5)]

key = generate_key()
name = generate_random_name()
file_reconstruction_threshold = 2
bootstrap = Bootstrap(key, name, file_reconstruction_threshold)


def teardown_function(function):
    cm.clear_user_credentials()


def test_size():
    assert Bootstrap.SIZE == len(str(bootstrap))


def test_roundtrip():
    BM = BootstrapManager(providers, 2)
    BM.distribute_bootstrap(bootstrap)
    assert BM.recover_bootstrap() == (bootstrap, len(providers))


def test_bad_configuration():
    BM = BootstrapManager(providers, 300)

    with pytest.raises(exceptions.LibraryException):
        BM.distribute_bootstrap(bootstrap)


def test_recover_fresh_providers():
    for provider in providers:
        provider.wipe()
    BM = BootstrapManager(providers, 3)
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_multiple_sessions():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    BM = BootstrapManager(providers, 3)
    assert BM.recover_bootstrap() == (bootstrap, len(providers))


def test_erase_recover():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[1].wipe()
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert sorted([failure.provider for failure in excinfo.value.failures]) == sorted(providers[0:2])


def test_erase_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    with pytest.raises(exceptions.FatalOperationFailure) as excinfo:
        BM.recover_bootstrap()
        assert sorted([failure.provider for failure in excinfo.value.failures]) == sorted(providers[0:3])


# TODO - once RSS is in, change this
def test_corrupt_share():
    # first share is corrupted
    shares = ['1,183,14383506571137248858752746226568890411g\x0086185201\xfb\x007694740488V\x00125062113802f\x0016825707182662m\x0026\xdb\x0058854018710391183134421389524070/\x006114646214168265060555k\x008494100800704202007671\xa4\x00555308', '1,182,226267014304695315817131242195232439865531487981907935014461971554172871990460346867510934666164763232525862557386126902981162041783990791288578655246013942868725078574167846906935987', '1,183,3357163050023212588368815536361544826733003297006665064895180759814132847129670262705551618197666027830022214551307496988058445575234341192490279578525025275650912442261552259227804692', '1,183,4368762778635742506151151092050888947118091043632084490648152100885284185985093519107623674690171107856581436127584550363491099012657101346202889318359445143868979619811567566041705169', '1,182,561066200142285069164137909263264801020794727858166212273375994767626888556730116073727104143680003312203527286217287029279122354052271252426407874749273547522926611224213767348637418']
    for share, provider in zip(shares, providers):
        provider.put(BootstrapManager.BOOTSTRAP_FILE_NAME, "share")

    BM = BootstrapManager(providers, 3)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


def modify_bootstrap_plaintext(provider, new_k=None, new_n=None, new_id=None):
    k, n, provider_id = provider.get(BootstrapManager.BOOTSTRAP_PLAINTEXT_FILE_NAME).split(",")
    new_k = k if new_k is None else new_k
    new_n = n if new_n is None else new_n
    new_id = provider_id if new_id is None else new_id
    string = ",".join(map(str, [new_k, new_n, new_id]))
    provider.put(BootstrapManager.BOOTSTRAP_PLAINTEXT_FILE_NAME, string)


def test_corrupt_k_recover():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:2]:
        modify_bootstrap_plaintext(provider, new_k=2)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert sorted([failure.provider for failure in excinfo.value.failures]) == sorted(providers[0:2])
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_corrupt_k_2_recover():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:2]:
        modify_bootstrap_plaintext(provider, new_k=4)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert sorted([failure.provider for failure in excinfo.value.failures]) == sorted(providers[0:2])
    assert BM.bootstrap_reconstruction_threshold == threshold


# outside our threat model, but malicious providers propose a threshold too high to support
def test_corrupt_k_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:3]:
        modify_bootstrap_plaintext(provider, new_k=4)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


# this actually won't fail - at this point, we are outside our threat model
def test_corrupt_k_but_not_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:4]:
        modify_bootstrap_plaintext(provider, new_k=4)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[4]
    assert BM.bootstrap_reconstruction_threshold == 4


def test_invalid_id():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=5)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[0]
    assert BM.bootstrap_reconstruction_threshold == 3
