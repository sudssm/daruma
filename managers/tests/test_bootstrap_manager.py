from managers.BootstrapManager import BootstrapManager, Bootstrap
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from managers.CredentialManager import CredentialManager
from tools.encryption import generate_key
from tools.utils import generate_random_name
import zlib
import json
import pytest

cm = CredentialManager()
cm.load()


def make_local(cm, path):
    provider = LocalFilesystemProvider(cm)
    provider.connect(path)
    return provider

providers = [make_local(cm, "tmp/" + str(i)) for i in xrange(5)]

key = generate_key()
name = generate_random_name()
file_reconstruction_threshold = 2
bootstrap = Bootstrap(key, name, file_reconstruction_threshold)


def teardown_function(function):
    cm.clear_user_credentials()


def modify_bootstrap_plaintext(provider, new_k=None, new_n=None, new_id=None, change_version=False):
    k, n, provider_id, version = zlib.decompress(provider.get(BootstrapManager.BOOTSTRAP_PLAINTEXT_FILE_NAME)).split(",")
    new_k = k if new_k is None else new_k
    new_n = n if new_n is None else new_n
    new_id = provider_id if new_id is None else new_id
    version = "foo" if change_version else version
    string = ",".join(map(str, [new_k, new_n, new_id, version]))
    provider.put(BootstrapManager.BOOTSTRAP_PLAINTEXT_FILE_NAME, zlib.compress(string))


def corrupt_share(provider):
    share = provider.get(BootstrapManager.BOOTSTRAP_FILE_NAME)
    data = json.loads(zlib.decompress(share))
    data["share"] += 1
    share = zlib.compress(json.dumps(data))
    provider.put(BootstrapManager.BOOTSTRAP_FILE_NAME, share)


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
    assert sorted(failure.provider for failure in excinfo.value.failures) == sorted(providers[0:2])


def test_erase_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    with pytest.raises(exceptions.FatalOperationFailure) as excinfo:
        BM.recover_bootstrap()
        assert sorted(failure.provider for failure in excinfo.value.failures) == sorted(providers[0:3])


def test_corrupt_share():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    # corrupt first share
    corrupt_share(providers[0])

    BM = BootstrapManager(providers, threshold)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert excinfo.value.failures[0].provider == providers[0]
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_corrupt_share_failure():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    for i in xrange(3):
        corrupt_share(providers[i])

    BM = BootstrapManager(providers, threshold)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


def test_corrupt_k_recover():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:2]:
        modify_bootstrap_plaintext(provider, new_k=2)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_corrupt_k_2_recover():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:2]:
        modify_bootstrap_plaintext(provider, new_k=4)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


# outside our threat model, but malicious providers propose a threshold too high to support
def test_corrupt_k_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:3]:
        modify_bootstrap_plaintext(provider, new_k=4)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


# outside our threat model so honest provider gets penalized
def test_corrupt_k_but_not_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    new_threshold = 4
    for provider in providers[0:4]:
        modify_bootstrap_plaintext(provider, new_k=new_threshold)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == new_threshold


def test_id_type_error():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id='m')

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[0]
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_impossible_ids():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=5)
    modify_bootstrap_plaintext(providers[1], new_id=-3)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 2
    assert sorted(failure.provider for failure in excinfo.value.failures) == sorted(providers[0:2])
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_one_duplicate_id_before():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=3)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_one_duplicate_id_after():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[4], new_id=3)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_two_duplicate_id():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=3)
    modify_bootstrap_plaintext(providers[1], new_id=3)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_multiple_duplicate_ids():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=3)
    modify_bootstrap_plaintext(providers[1], new_id=4)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_swap_ids():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=1)
    modify_bootstrap_plaintext(providers[1], new_id=0)

    assert BM.recover_bootstrap() == (bootstrap, len(providers))
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_replace_ids():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    modify_bootstrap_plaintext(providers[0], new_id=10)
    modify_bootstrap_plaintext(providers[1], new_id=0)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[0]
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_corrupt_bootstrap():
    threshold = 3
    BM = BootstrapManager(providers, threshold)
    BM.distribute_bootstrap(bootstrap)

    providers[0].put(BootstrapManager.BOOTSTRAP_FILE_NAME, "foo")

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()
    assert excinfo.value.result == (bootstrap, len(providers))
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[0]
    assert BM.bootstrap_reconstruction_threshold == threshold


def test_ids_out_of_range_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:3]:
        modify_bootstrap_plaintext(provider, new_id=10)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


def test_ids_in_range_fail():
    BM = BootstrapManager(providers, 3)
    BM.distribute_bootstrap(bootstrap)

    for provider in providers[0:3]:
        modify_bootstrap_plaintext(provider, new_id=4)

    with pytest.raises(exceptions.FatalOperationFailure):
        BM.recover_bootstrap()


def test_one_corrupt_one_old():
    BM = BootstrapManager(providers[:4], 3)
    BM.distribute_bootstrap(bootstrap)

    # first provider becomes outdated, but has right params
    BM = BootstrapManager(providers[1:], 3)
    BM.distribute_bootstrap(bootstrap)

    # second provider is corrupt
    corrupt_share(providers[1])

    # try and recover with all providers
    BM = BootstrapManager(providers, -1)  # this threshold doesn't matter
    with pytest.raises(exceptions.OperationFailure) as excinfo:
        BM.recover_bootstrap()

    # only bad provider is 1, but 0 wasn't used to reconstruct
    assert excinfo.value.result == (bootstrap, 4)
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[1]
