import sys
import threading
from gui.webview_server.server import start_ui_server, WEBVIEW_SERVER_HOST, WEBVIEW_SERVER_PORT
from gui.webview_client.app import SBApp


def platform_specific_setup():
    """
    Run code specific to the host OS to set up our app.
    """
    if sys.platform.startswith('darwin'):
        # On OSX, we need to give ourselves an App Transport Security exception
        # so that we can read data from localhost over HTTP.
        import AppKit
        import Foundation
        bundle = AppKit.NSBundle.mainBundle()
        info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
        info['NSAppTransportSecurity'] = {'NSAllowsArbitraryLoads': Foundation.YES}

if __name__ == "__main__":
    platform_specific_setup()

    # Initialize native UI
    app = SBApp((WEBVIEW_SERVER_HOST, WEBVIEW_SERVER_PORT), setup_complete=False)

    # Start HTTP UI server
    ui_server_thread = threading.Thread(target=start_ui_server, args=(app,),
                                        name="ui_server_thread")
    ui_server_thread.daemon = True
    ui_server_thread.start()

    # Start native UI
    app.MainLoop()
