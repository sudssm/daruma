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


class MainAppMenu(wx.TaskBarIcon):
    def __init__(self, app_frame, host):
        """
        Args:
            app_frame: A frame for the enclosing app to be closed on exit.
            host: The (hostname, port) tuple for the UI server.
        """
        super(MainAppMenu, self).__init__()
        self.app_frame = app_frame  # Stored to close the app with
        self.host = host

        icon_path = pkg_resources.resource_filename(__name__, ICON_NAME)
        icon = wx.IconFromBitmap(wx.Bitmap(icon_path))
        self.SetIcon(icon, ICON_HOVERTEXT)

    def CreatePopupMenu(self):
        """
        Called when the taskbar icon is opened.
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
        webview.WebviewWindow(get_url_for_host(self.host, "providers")).Show()

    def on_exit(self, event):
        """
        Called with the quit item is selected.
        """
        wx.CallAfter(self.Destroy)
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
