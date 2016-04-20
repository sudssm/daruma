import shutil
# configuration for pytest


def pytest_sessionfinish(session, exitstatus):
    try:
        shutil.rmtree("tmp")
    except:
        pass
