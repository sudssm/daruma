import subprocess
import sys


def build_app():
    """
    Builds a new application.
    """
    def build_app_osx():
        subprocess.call(["python", "setup.py", "py2app"])
    if sys.platform.startswith('darwin'):
        build_app_osx()
    else:
        sys.stderr.write("Fatal error: Unsupported platform")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
