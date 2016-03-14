import threading
from gui.webview_server.server import start_ui_server
from gui.osx.app import run_app

if __name__ == "__main__":
    ui_server_thread = threading.Thread(target=start_ui_server, name="ui_server_thread")
    ui_server_thread.daemon = True
    ui_server_thread.start()
    run_app()
