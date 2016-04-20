import os
import pkg_resources
import wx
import gui
import gui.webview_client.webview as webview
from tools.utils import APP_NAME

ICON_NAME = os.path.join("icons", "menubar.png")
ICON_HOVERTEXT = APP_NAME


def get_url_for_host(host, endpoint=""):
    """
    Returns the url to view for the given host and endpoint.

    Args:
        host: The (hostname, port) tuple for the UI server.
        endpoint: The optional endpoint to be viewed.
    """
    return "http://" + host[0] + ":" + str(host[1]) + "/" + endpoint


class WindowManager(object):
    """
    Contains references to all windows in use by the application.
    To use, add windows to the enclosed windows dictionary.
    """
    def __init__(self):
        self.windows = {}

    def close_all(self):
        """
        Closes all tracked windows and resets the WindowManager.
        """
        for window in self.windows.values():
            window.Close()
        self.windows = {}


class MainAppMenu(wx.TaskBarIcon):
    def __init__(self, app_frame, host):
        """
        Args:
            app_frame: A frame for the enclosing app (to be closed on exit).
            host: The (hostname, port) tuple for the UI server.
        """
        super(MainAppMenu, self).__init__()
        self.app_frame = app_frame
        self.host = host

        icon_stream = pkg_resources.resource_stream(gui.__name__, ICON_NAME)
        icon = wx.IconFromBitmap(wx.ImageFromStream(icon_stream).ConvertToBitmap())
        self.SetIcon(icon, ICON_HOVERTEXT)

        self.window_manager = WindowManager()

    def CreatePopupMenu(self):
        """
        Automatically called when the taskbar icon is clicked.
        Overriden from superclass.
        """
        menu = wx.Menu()

        if self.setup_complete:
            providers_item = menu.Append(wx.ID_ANY, "Providers")
            menu.Bind(wx.EVT_MENU, self.generate_webview_handler("dashboard.html"), providers_item)
        else:
            setup_item = menu.Append(wx.ID_ANY, "Continue setup")
            menu.Bind(wx.EVT_MENU, self.generate_webview_handler("setup.html"), setup_item)

        menu.AppendSeparator()

        exit_item = menu.Append(wx.ID_EXIT)
        menu.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        return menu

    def generate_webview_handler(self, endpoint):
        def on_open_webview(event):
            """
            Opens the specified webview.
            """
            def open_modal_factory(window):
                matching_url = get_url_for_host(self.host, "modal/show/")

                def on_request_resource(event):
                    """
                    Filters all full page redirects for the keyword URL to open
                    a modal.
                    """
                    if event.GetURL().startswith(matching_url):
                        target_endpoint = event.GetURL()[len(matching_url):]
                        event.Veto()
                        self.open_webview_modal_for(window, target_endpoint)
                return on_request_resource

            def on_close_webview(event):
                window = self.window_manager.windows.pop(endpoint)
                window.Destroy()
            window = self.window_manager.windows.get(endpoint)
            if window is None:
                window = webview.WebviewWindow(get_url_for_host(self.host, endpoint))
                self.window_manager.windows[endpoint] = window
                window.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, open_modal_factory(window))
                window.Bind(wx.EVT_CLOSE, on_close_webview)
                window.CenterOnScreen()
                window.Show()
            else:
                # TODO: bring app to foreground
                window.Raise()
        return on_open_webview

    def open_webview_modal_for(self, target_window, modal_endpoint):
        """
        Opens a modal window under the target_window pointing to the URL
        referenced by modal_endpoint/
        """
        def close_listener_factory(dialog):
            def on_request_resource(event):
                """
                Filters all full page redirects for the keyword URL to close
                the modal.
                """
                if event.GetURL() == get_url_for_host(self.host, "modal/close"):
                    event.Veto()
                    dialog.Close()
            return on_request_resource

        def on_close_modal_webview(event):
            dialog = event.GetDialog()
            dialog.Destroy()
        dialog = webview.WebviewModal(url=get_url_for_host(self.host, modal_endpoint),
                                      size=(500, 500),
                                      parent=target_window)
        dialog.Bind(wx.html2.EVT_WEBVIEW_NAVIGATING, close_listener_factory(dialog))
        self.Bind(wx.EVT_WINDOW_MODAL_DIALOG_CLOSED, on_close_modal_webview)
        dialog.ShowWindowModal()

    def on_exit(self, event):
        """
        Called when the quit item is selected.
        """
        wx.CallAfter(self.Destroy)
        self.window_manager.close_all()
        self.app_frame.Close()


class DarumaApp(wx.App):
    def __init__(self, host, setup_complete=False):
        """
        To begin using the app, call this object's MainLoop() method.

        Args:
            host: The (hostname, port) tuple for the UI server.
            setup_complete: See mark_setup_complete().  Defaults to False in
                this method.
        """
        self.host = host
        self.setup_complete = setup_complete
        super(DarumaApp, self).__init__(redirect=False)

    def OnInit(self):
        """
        A standard wxPython method.  Do not call directly.
        """
        frame = wx.Frame(parent=None)
        self.SetTopWindow(frame)
        self.menu = MainAppMenu(frame, self.host)
        self.menu.setup_complete = self.setup_complete
        return True

    def mark_setup_complete(self, is_complete=True):
        """
        Whether the menu should expose the provider dashboard or should instead
        prompt the user to finish setup.  Defaults to True.
        """
        self.menu.setup_complete = is_complete
