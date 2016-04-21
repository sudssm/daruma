import logging
import sys
import threading
from custom_exceptions import exceptions
from driver.Daruma import Daruma
from gui.filesystem.FilesystemWatcher import FilesystemWatcher
from gui.webview_server.server import start_ui_server
from gui.webview_client.app import DarumaApp
from managers.ProviderManager import ProviderManager
from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT, get_app_folder, make_app_folder


class ApplicationState(object):
    """
    If the Daruma field is not None, then the application has been set up and
    it contains a valid Daruma object.
    Otherwise, the providers field must be set with a list of
    providers with valid authentication.
    """
    def __init__(self):
        self.daruma = None
        self.provider_manager = ProviderManager()
        self.providers = []
        self.needs_reprovision = False
        self.filesystem_watcher = None


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
    app_menu = DarumaApp((INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT),
                         setup_complete=(app_state.daruma is not None))

    # Start HTTP UI server
    ui_server_thread = threading.Thread(target=start_ui_server,
                                        args=(app_menu, app_state),
                                        name="ui_server_thread")
    ui_server_thread.daemon = True
    ui_server_thread.start()

    # Start filesystem watcher
    make_app_folder()
    app_state.filesystem_watcher = FilesystemWatcher(get_app_folder(), app_state)
    app_state.filesystem_watcher.bulk_update_from_filesystem()
    filesystem_watcher_thread = threading.Thread(target=app_state.filesystem_watcher.start(),
                                                 name="filesytem_watcher_thread")
    filesystem_watcher_thread.daemon = True
    filesystem_watcher_thread.start()

    # Start native UI
    app_menu.MainLoop()
    app_state.filesystem_watcher.stop()


if __name__ == "__main__":
    logging.basicConfig(filename='daruma_run.log', filemode='w', level=logging.DEBUG)

    platform_specific_setup()

    app_state = ApplicationState()
    providers, _ = app_state.provider_manager.load_all_providers_from_credentials()
    try:
        assert len(providers) >= 2
        app_state.daruma, extra_providers = Daruma.load(providers)
        app_state.providers = providers
        app_state.needs_reprovision = len(extra_providers) > 0 or len(app_state.daruma.get_missing_providers()) > 0
    except (AssertionError, exceptions.FatalOperationFailure):
        app_state.providers = providers
    launch_gui(app_state)
