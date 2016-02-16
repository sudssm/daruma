import rumps
import webview
from gui.webview_server.server import SERVER_HOST, SERVER_PORT

BASE_SERVER_URL = "http://" + SERVER_HOST + ":" + str(SERVER_PORT)


class StatusBarApp(rumps.App):
    @rumps.clicked("Providers")
    def prefs(self, _):
        webview.create_window("Providers", BASE_SERVER_URL + "/providers", resizable=False)


def run_app():
    StatusBarApp("SecretBox").run()
