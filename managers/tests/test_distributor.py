from managers.Distributor import FileDistributor
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from tools.encryption import generate_key
import pytest

providers = [LocalFilesystemProvider("tmp/" + str(i)) for i in xrange(5)]


def setup_function(function):
    for provider in providers:
        provider.wipe()


def test_get_nonexisting():
    for provider in providers:
        provider.wipe()

    FD = FileDistributor(providers, 3)
    try:
        FD.get("test", "dummy")
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_roundtrip():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    key2 = FD.put("another", "data2")
    assert FD.get("test", key) == "data"
    assert FD.get("another", key2) == "data2"


def test_roundtrip_with_key():
    key = generate_key()
    FD = FileDistributor(providers, 3)
    FD.put("test", "data", key)
    assert FD.get("test", key) == "data"


def test_delete():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    FD.delete("test")
    try:
        FD.get("test", key)
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 5


def test_update():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    key = FD.put("test", "other")
    assert FD.get("test", key) == "other"


def test_corrupt_recover():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    providers[0].wipe()
    providers[2].wipe()
    try:
        FD.get("test", key)
        assert False
    except exceptions.OperationFailure as e:
        assert e.result == "data"
        assert len(e.failures) == 2


def test_corrupt_fail():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    providers[0].wipe()
    providers[1].wipe()
    providers[2].wipe()
    try:
        FD.get("test", key)
        assert False
    except exceptions.FatalOperationFailure as e:
        assert len(e.failures) == 3


def test_mutate_recover():
    # the first share is bad!
    shares = ['\x00\x00\x00\x00\x13\x00\xd0\x00\x00\x00\x00\x00,\x00\xe2\x00R\x00\x00\x00\x01\x00\x00\x00\xdd\x00\x00\x00\x00\x00\x00\x00\x87\x00\x00\x00\x00\x00\x00\x00[\x00\x00\x00\x00\x00\x00\x00\x00\x00(\x00\x00\x00\x06\x00\x00\x01\x96\x00^\x0c\x0b\x02\x01\x01\xa5\x00\xb2\x00A\x00\x10\x00\xa8\x00\x00\x00\xf9\x00\x1dP\xf8\xc10\x00=\xdc>)\x7f\xb7c\x00\xb3\x03', '\x01\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x9b\x08\xdcW\x1c\xaco\xba<\xff\x87\xca\xa2\xf1\xdc\x0c', '\x02\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8eN6\xc2(\x8eI\x13\xd2\xbd\xdf8\x00\x00\x00\x00', "\x03\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x16\x12Toj\x1bu\xd0k'EP\x04o\x0f", '\x04\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00Q\xf3P8n\xaf\x9e]a\xb3\x7fyH\xcbaq']
    key = "%\xae\xbc\x15\t)\xb7\x19\x89\xe4^\xdd\xda>[J\xb1\xaag\x8f\x94\x9b\xe3\xad\xd8*{D\xf8.\xb4\xdf"
    for share, provider in zip(shares, providers):
        provider.put("test", share)

    FD = FileDistributor(providers, 3)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FD.get("test", key)

    assert excinfo.value.result == "data"
    assert len(excinfo.value.failures) == 1
    assert excinfo.value.failures[0].provider == providers[0]


def test_mutate_two_recover():
    # shares at indices 2 and 3 are bad!
    shares = ['\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x0eu\xa7\\\xef\xdb\rg\xab,hI\xdb\x14\xe1', '\x01\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\xc3_\xa1\xa29c\x19w\xfc\xdeI\xf4\xd1/%', '\x02\x00\x00\x00\x10\x00\x00\x00"\x00\x00\x00\x92\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00Z\x00\x00\x00\x00\x00\x00\x00\xe4\x00\xbd\x00\x9d\x00\x00\x00\x00\x00\x00\x006\x00\xde\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~\x00\x00\x00\x87tk\x80\xea\x00\x8c\x0fC\xe1\x9a\x00\x1d\x00h\x00', '\r\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00}\x00\x00\x00\x01\x00\x00\x00\x00\x00\xe5\x00\xbe\x00\x00\x00F\x00\xf5\x00\x00\x00\x00\x00\xde\x00\x00\x00\x00\x00\xfa\x00\x00\x00\x00\x00\x00\x00\x06\x00\xbe\x00\x00\xcc^\x0c\x0b\x02\xbb\x009\x00-\x00\x0e\x00\x00\x00\x00\x00\x00\x00s\x00\xc1\xb90\x00O\xcbe\x00S\xb6\xb0*\xbd\n}\x00', '\x04\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf3\x0baD\xee6\xe9\xa5"\x9f\xd8,\x01u\x98\xc6']
    key = "%\xae\xbc\x15\t)\xb7\x19\x89\xe4^\xdd\xda>[J\xb1\xaag\x8f\x94\x9b\xe3\xad\xd8*{D\xf8.\xb4\xdf"
    for share, provider in zip(shares, providers):
        provider.put("test", share)

    FD = FileDistributor(providers, 3)

    with pytest.raises(exceptions.OperationFailure) as excinfo:
        FD.get("test", key)
    assert excinfo.value.result == "data"
    assert sorted([f.provider for f in excinfo.value.failures]) == sorted([providers[2], providers[3]])


def test_mutate_fail():
    # shares at indices 2, 3 and 4 are bad!
    shares = ['\x00\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00 \x0eu\xa7\\\xef\xdb\rg\xab,hI\xdb\x14\xe1', '\x01\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00f\xc3_\xa1\xa29c\x19w\xfc\xdeI\xf4\xd1/%', '\x02\x00\x00\x00\x10\x00\x00\x00"\x00\x00\x00\x92\x00\x00\x00\x00\x00\x00\x00\xbf\x00\x00\x00Z\x00\x00\x00\x00\x00\x00\x00\xe4\x00\xbd\x00\x9d\x00\x00\x00\x00\x00\x00\x006\x00\xde\x00\x00\x00\x00\x00\x00\x00L\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00~\x00\x00\x00\x87tk\x80\xea\x00\x8c\x0fC\xe1\x9a\x00\x1d\x00h\x00', '\r\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00}\x00\x00\x00\x01\x00\x00\x00\x00\x00\xe5\x00\xbe\x00\x00\x00F\x00\xf5\x00\x00\x00\x00\x00\xde\x00\x00\x00\x00\x00\xfa\x00\x00\x00\x00\x00\x00\x00\x06\x00\xbe\x00\x00\xcc^\x0c\x0b\x02\xbb\x009\x00-\x00\x0e\x00\x00\x00\x00\x00\x00\x00s\x00\xc1\xb90\x00O\xcbe\x00S\xb6\xb0*\xbd\n}\x00', '\x04\x00\x00\x00\x10\x00\x00\x00\x00\x00\x00\x00,\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x01\x00\xcc^\x0c\x0b\x02\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x10\xf3\x0baD\xef6\xe9\xa5"\x9f\xd8,\x01u\x98\xc6']
    key = "%\xae\xbc\x15\t)\xb7\x19\x89\xe4^\xdd\xda>[J\xb1\xaag\x8f\x94\x9b\xe3\xad\xd8*{D\xf8.\xb4\xdf"
    for share, provider in zip(shares, providers):
        provider.put("test", share)

    FD = FileDistributor(providers, 3)

    with pytest.raises(exceptions.FatalOperationFailure):
        FD.get("test", key)


def test_wrong_key():
    wrong_key = generate_key()
    FD = FileDistributor(providers, 3)
    FD.put("test", "data")
    with pytest.raises(exceptions.FatalOperationFailure):
        FD.get("test", wrong_key)


def test_multiple_sessions():
    FD = FileDistributor(providers, 3)
    key = FD.put("test", "data")
    FD = FileDistributor(providers, 3)
    assert FD.get("test", key) == "data"
