import os
import pkg_resources
import wx
import gui
import gui.webview_client.webview as webview

ICON_NAME = os.path.join("icons", "menubar.png")
ICON_HOVERTEXT = "trust-no-one"


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

        icon_stream = pkg_resources.resource_stream(__name__, ICON_NAME)
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
            menu.Bind(wx.EVT_MENU, self.generate_webview_handler("providers"), providers_item)
        else:
            setup_item = menu.Append(wx.ID_ANY, "Continue setup")
            menu.Bind(wx.EVT_MENU, self.generate_webview_handler("setup"), setup_item)

        menu.AppendSeparator()

        exit_item = menu.Append(wx.ID_EXIT)
        menu.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        return menu

    def generate_webview_handler(self, endpoint):
        def on_open_webview(event):
            """
            Opens the specified webview.
            """
            def on_close_webview(event):
                window = self.window_manager.windows.pop(endpoint)
                window.Destroy()
            window = self.window_manager.windows.get(endpoint)
            if window is None:
                window = webview.WebviewWindow(get_url_for_host(self.host, endpoint))
                self.window_manager.windows[endpoint] = window
                window.Bind(wx.EVT_CLOSE, on_close_webview)
                window.CenterOnScreen()
                window.Show()
            else:
                # TODO: bring app to foreground
                window.Raise()
        return on_open_webview

    def on_exit(self, event):
        """
        Called when the quit item is selected.
        """
        wx.CallAfter(self.Destroy)
        self.window_manager.close_all()
        self.app_frame.Close()


class SBApp(wx.App):
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
        super(SBApp, self).__init__(redirect=False)

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
