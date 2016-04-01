import os
import pkg_resources
import wx
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

        icon_path = pkg_resources.resource_filename(__name__, ICON_NAME)
        icon = wx.IconFromBitmap(wx.Bitmap(icon_path))
        self.SetIcon(icon, ICON_HOVERTEXT)

        self.window_manager = WindowManager()

    def CreatePopupMenu(self):
        """
        Automatically called when the taskbar icon is clicked.
        Overriden from superclass.
        """
        menu = wx.Menu()

        providers_item = menu.Append(wx.ID_ANY, "Providers")
        menu.Bind(wx.EVT_MENU, self.on_open_providers, providers_item)

        menu.AppendSeparator()

        exit_item = menu.Append(wx.ID_EXIT)
        menu.Bind(wx.EVT_MENU, self.on_exit, exit_item)

        return menu

    def on_open_providers(self, event):
        """
        Opens the provider dashboard webview.
        """
        def on_close_providers(event):
            provider_window = self.window_manager.windows.pop("providers")
            provider_window.Destroy()
        provider_window = self.window_manager.windows.get("providers")
        if provider_window is None:
            provider_window = webview.WebviewWindow(get_url_for_host(self.host, "providers"))
            self.window_manager.windows["providers"] = provider_window
            provider_window.Bind(wx.EVT_CLOSE, on_close_providers)
            provider_window.CenterOnScreen()
            provider_window.Show()
        else:
            # TODO: bring app to foreground
            provider_window.Raise()

    def on_exit(self, event):
        """
        Called when the quit item is selected.
        """
        wx.CallAfter(self.Destroy)
        self.window_manager.close_all()
        self.app_frame.Close()


class SBApp(wx.App):
    def __init__(self, host):
        """
        Args:
            host: The (hostname, port) tuple for the UI server.
        """
        self.host = host
        super(SBApp, self).__init__(redirect=False)

    def OnInit(self):
        frame = wx.Frame(parent=None)
        self.SetTopWindow(frame)
        MainAppMenu(frame, self.host)
        return True


def run_app(host):
    """
    Args:
        host: The (hostname, port) tuple for the UI server.
    """
    app = SBApp(host)
    app.MainLoop()
