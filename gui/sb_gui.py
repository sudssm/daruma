import sys
import threading
from custom_exceptions import exceptions
from driver.SecretBox import SecretBox
from gui.webview_server.server import start_ui_server
from gui.webview_client.app import SBApp
from managers.ProviderManager import ProviderManager
from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT


class ApplicationState(object):
    """
    If the secretbox field is not None, then the application has been set up and
    it contains a valid SecretBox object.
    Otherwise, the prelaunch_providers field must be set with a list of
    providers with valid authentication.
    """
    secretbox = None
    prelaunch_providers = []


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


def launch_gui(app_state):
    # Initialize native UI
    app_menu = SBApp((INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT),
                     setup_complete=(app_state.secretbox is not None))

    # Start HTTP UI server
    ui_server_thread = threading.Thread(target=start_ui_server,
                                        args=(app_menu, app_state),
                                        name="ui_server_thread")
    ui_server_thread.daemon = True
    ui_server_thread.start()

    # Start native UI
    app_menu.MainLoop()


if __name__ == "__main__":
    platform_specific_setup()

    providers, _ = ProviderManager().load_all_providers_from_credentials()
    app_state = ApplicationState()
    try:
        assert len(providers) >= 2
        app_state.secretbox = SecretBox.load(providers)
    except (AssertionError, exceptions.FatalOperationFailure):
        app_state.prelaunch_providers = providers
    launch_gui(app_state)
