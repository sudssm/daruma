import errno
import os
import shutil
from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider


class TestProviderState:
    ACTIVE, OFFLINE, UNAUTHENTICATED, FAILING, CORRUPTING = \
        "ACTIVE", "OFFLINE", "UNAUTHENTICATED", "FAILING", "CORRUPTING"


class TestProvider(LocalFilesystemProvider):
    def __init__(self, provider_path="", state=TestProviderState.ACTIVE):
        self.state = state
        super(TestProvider, self).__init__(provider_path)

    def _check_state(self, check_failing=True):
        if self.state == TestProviderState.OFFLINE:
            raise exceptions.ConnectionFailure(self)
        if self.state == TestProviderState.UNAUTHENTICATED:
            raise exceptions.AuthFailure(self)
        if check_failing and self.state == TestProviderState.FAILING:
            raise exceptions.ProviderOperationFailure()

    def connect(self):
        self._check_state(check_failing=False)
        super(TestProvider, self).connect()

    def get(self, filename):
        self._check_state()

        result = super(TestProvider, self).get(filename)
        if self.state == TestProviderState.MALICIOUS:
            # TODO mutate file
            pass
        return result

    def put(self, filename, data):
        self._check_state()
        return super(TestProvider, self).put(filename, data)

    def delete(self, filename):
        self._check_state()
        return super(TestProvider, self).delete(filename)

    def wipe(self):
        self._check_state()
        return super(TestProvider, self).wipe()

    def __str__(self):
        return "<TestFilesystemProvider@" + self.provider_path + "-" + self.state + ">"
