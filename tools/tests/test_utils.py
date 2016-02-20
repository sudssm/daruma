import sys
from custom_exceptions import exceptions
import tools.utils
import pytest


def test_successful_sandbox():
    def good_function(name):
        return [name, name.upper()]
    test_name = "fred"
    result = tools.utils.sandbox_function(good_function, test_name)
    assert result == [test_name, test_name.upper()]


def test_sandbox_with_exception():
    def bad_function(name):
        return 1 / 0
    test_name = "fred"
    with pytest.raises(exceptions.SandboxProcessFailure) as excinfo:
        tools.utils.sandbox_function(bad_function, test_name)
    assert excinfo.value.exitcode == 1


def test_sandbox_with_exit_code():
    EXIT_CODE = 7

    def exit_with_code(name):
        sys.exit(EXIT_CODE)
    test_name = "fred"
    with pytest.raises(exceptions.SandboxProcessFailure) as excinfo:
        tools.utils.sandbox_function(exit_with_code, test_name)
    assert excinfo.value.exitcode == EXIT_CODE


def test_sandbox_with_segfault():
    SEGFAULT_CODE = -11

    def cause_segfault():
        """
        Crashes Python using an example from https://wiki.python.org/moin/CrashingPython
        """
        import ctypes
        i = ctypes.c_char('a')
        j = ctypes.pointer(i)
        c = 0
        while True:
                j[c] = 'a'
                c += 1
        j
    with pytest.raises(exceptions.SandboxProcessFailure) as excinfo:
        tools.utils.sandbox_function(cause_segfault)
    assert excinfo.value.exitcode == SEGFAULT_CODE
