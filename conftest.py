import shutil
# configuration for pytest


def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree("tmp")
