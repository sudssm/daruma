from demo_provider.client.TestServerProvider import TestServerProvider
from providers.BaseProvider import BaseProvider
from custom_exceptions import exceptions
from demo_provider.server import app
from threading import Thread
import pytest


# start a demo instance of a server
server_thread = Thread(target=app.run)
server_thread.setDaemon(True)
server_thread.start()


def test_wipe():
    FS = TestServerProvider("127.0.0.1", 5000)
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file2")


def test_roundtrip():
    FS = TestServerProvider("127.0.0.1", 5000)
    FS.put("file1", "abc")
    assert FS.get("file1") == "abc"


def test_exception_has_provider():
    try:
        FS = TestServerProvider("127.0.0.1", 5000)
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = TestServerProvider("127.0.0.1", 5000)
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = TestServerProvider("127.0.0.1", 5000)
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = TestServerProvider("127.0.0.1", 5000)
    FS.wipe()
    FS.put("file1", "abc")
    FS = TestServerProvider("127.0.0.1", 5000)
    assert FS.get("file1") == "abc"
