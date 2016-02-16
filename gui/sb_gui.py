import sys
import threading
from custom_exceptions.exceptions import UnsupportedPlatformException
from gui.webview_server.server import start_ui_server
from gui.platforms.osx.app import run_app as run_app_osx


def start_gui_across_platforms():
    if sys.platform.startswith('darwin'):
        run_app_osx()
    else:
        raise UnsupportedPlatformException("No support for " + sys.platform)

if __name__ == "__main__":
    ui_server_thread = threading.Thread(target=start_ui_server, name="ui_server_thread")
    ui_server_thread.daemon = True
    ui_server_thread.start()
    start_gui_across_platforms()
