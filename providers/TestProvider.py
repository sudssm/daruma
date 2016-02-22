from custom_exceptions import exceptions
from providers.LocalFilesystemProvider import LocalFilesystemProvider
from contextlib import contextmanager
from struct import pack
from random import randint, random, randrange


class TestProviderState:
    ACTIVE, OFFLINE, UNAUTHENTICATED, FAILING, CORRUPTING = \
        "ACTIVE", "OFFLINE", "UNAUTHENTICATED", "FAILING", "CORRUPTING"


class TestProvider(LocalFilesystemProvider):
    def __init__(self, provider_path=""):
        self.state = TestProviderState.ACTIVE
        self.state_timer = 0
        super(TestProvider, self).__init__(provider_path)

    def set_state(self, state, requests=-1):
        """
        Set the state of the provider
        The state will return to ACTIVE after (requests) function calls
        or never if requests is -1
        """
        if state != TestProviderState.UNAUTHENTICATED:
            self.authenticated = True
        self.state = state
        self.state_timer = requests

    @contextmanager
    def exception_handler(self, check_failing=True):
        self.state_timer -= 1
        if self.state_timer == 0:
            self.state = TestProviderState.ACTIVE

        if self.state == TestProviderState.OFFLINE:
            raise exceptions.ConnectionFailure(self)
        if self.state == TestProviderState.UNAUTHENTICATED:
            raise exceptions.AuthFailure(self)
        if check_failing and self.state == TestProviderState.FAILING:
            raise exceptions.ProviderOperationFailure(self)
        yield

    def connect(self):
        with self.exception_handler(check_failing=False):
            super(TestProvider, self).connect()

    def get(self, filename):
        with self.exception_handler():
            result = super(TestProvider, self).get(filename)
        if self.state == TestProviderState.CORRUPTING:
            if random() > 0.5:
                size = randrange(50)*2
            else:
                size = len(result)/2
            corrupt = pack("h"*size, *[randint(0, 255) for i in xrange(size)])
            return "".join(corrupt)
        else:
            return result

    def put(self, filename, data):
        with self.exception_handler():
            return super(TestProvider, self).put(filename, data)

    def delete(self, filename):
        with self.exception_handler():
            return super(TestProvider, self).delete(filename)

    def wipe(self):
        with self.exception_handler():
            return super(TestProvider, self).wipe()

    def __str__(self):
        return "<TestProvider@" + self.provider_path + "-" + self.state + "-" + self.status + ">"
