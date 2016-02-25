from managers.BootstrapManager import BootstrapManager, Bootstrap
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
from tools.utils import generate_filename
from struct import pack
from random import randint
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]

key = generate_key()
name = generate_filename()
file_reconstruction_threshold = 2
bootstrap = Bootstrap(key, name, file_reconstruction_threshold)


def test_size():
    assert Bootstrap.SIZE == len(str(bootstrap))


def test_roundtrip():
    BM = BootstrapManager(providers, 2)
    BM.distribute_bootstrap(bootstrap)
    assert BM.recover_bootstrap() == bootstrap


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
    assert BM.recover_bootstrap() == bootstrap


def test_erase_recover():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[2].wipe()
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == bootstrap
        assert len(e.failures) == 2


def test_erase_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    try:
        BM.recover_bootstrap()
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3


# TODO - once RSS is in, change this
def test_corrupt_share():
    # first share is corrupted
    shares = ['\xbb\x00183,14383506571137248858752746226568890411g\x0086185201\xfb\x007694740488V\x00125062113802f\x0016825707182662m\x0026\xdb\x0058854018710391183134421389524070/\x006114646214168265060555k\x008494100800704202007671\xa4\x00555308', '1,182,226267014304695315817131242195232439865531487981907935014461971554172871990460346867510934666164763232525862557386126902981162041783990791288578655246013942868725078574167846906935987', '1,183,3357163050023212588368815536361544826733003297006665064895180759814132847129670262705551618197666027830022214551307496988058445575234341192490279578525025275650912442261552259227804692', '1,183,4368762778635742506151151092050888947118091043632084490648152100885284185985093519107623674690171107856581436127584550363491099012657101346202889318359445143868979619811567566041705169', '1,182,561066200142285069164137909263264801020794727858166212273375994767626888556730116073727104143680003312203527286217287029279122354052271252426407874749273547522926611224213767348637418']
    for share, provider in zip(shares, providers):
        provider.put(BootstrapManager.BOOTSTRAP_FILE_NAME, "share")

    BM = BootstrapManager(providers, 3)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


def test_corrupt_k():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    providers[0].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "2")
    providers[1].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "2")

    assert BM.recover_bootstrap() == bootstrap

def test_corrupt_k_2():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    providers[0].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "1")
    providers[1].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "1")

    assert BM.recover_bootstrap() == bootstrap


# outside our threat model, but clearly impossible
def test_corrupt_k_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    providers[0].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "4")
    providers[1].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "4")
    providers[2].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "4")

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


# this actually won't fail - at this point, we are outside our threat model
def test_corrupt_k_but_not_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    providers[0].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "3")
    providers[1].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "3")
    providers[2].put(BootstrapManager.BOOTSTRAP_THRESHOLD_FILE_NAME, "3")

    assert BM.recover_bootstrap() == bootstrap
