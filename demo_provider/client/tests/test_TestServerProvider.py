from demo_provider.client.TestServerProvider import TestServerProvider
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions
from demo_provider.server import app
from threading import Thread
import zlib
import pytest

cm = CredentialManager()
cm.load()

# start a demo instance of a server
server_thread = Thread(target=app.run)
server_thread.setDaemon(True)
server_thread.start()


def teardown_function(function):
    cm.clear_user_credentials()


def test_wipe():
    FS = TestServerProvider(cm)
    FS.connect("http://127.0.0.1:5000")
    FS.put("file1", "abc")
    FS.put("file2", "def")
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file2")


def test_roundtrip():
    FS = TestServerProvider(cm)
    FS.connect("http://127.0.0.1:5000")
    FS.put("file1", zlib.compress("abc"))
    assert zlib.decompress(FS.get("file1")) == "abc"


def test_exception_has_provider():
    try:
        FS = TestServerProvider(cm)
        FS.connect("http://127.0.0.1:5000")
        FS.wipe()
        FS.get("file1")
        assert False
    except exceptions.ProviderOperationFailure as e:
        assert e.provider == FS


def test_get_nonexisting():
    FS = TestServerProvider(cm)
    FS.connect("http://127.0.0.1:5000")
    FS.wipe()
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_delete():
    FS = TestServerProvider(cm)
    FS.connect("http://127.0.0.1:5000")
    FS.put("file1", "abc")
    FS.delete("file1")
    with pytest.raises(exceptions.ProviderOperationFailure):
        FS.get("file1")


def test_multiple_sessions():
    FS = TestServerProvider(cm)
    FS.connect("http://127.0.0.1:5000")
    FS.wipe()
    FS.put("file1", "abc")
    providers, _ = TestServerProvider.load_cached_providers(cm)
    FS = providers[0]
    assert FS.get("file1") == "abc"
