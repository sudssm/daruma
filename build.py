import subprocess
import sys


def build_app():
    """
    Builds a new application.
    """
    def build_app_osx():
        subprocess.call(["python", "setup.py", "py2app"])
        subprocess.call(["xcodebuild", "-target", "FileSyncClient"], cwd="gui/file_sync_status/osx")
        subprocess.call(["mkdir", "dist/daruma.app/Contents/PlugIns"])
        subprocess.call(["cp", "-r", "gui/file_sync_status/osx/build/Release/FileSyncClient.appex", "dist/daruma.app/Contents/PlugIns/"])
    if sys.platform.startswith('darwin'):
        build_app_osx()
    else:
        sys.stderr.write("Fatal error: Unsupported platform")
        sys.exit(1)


if __name__ == "__main__":
    build_app()
