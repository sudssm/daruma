import os
import pkg_resources
import wx
from gui.webview_server.server import SERVER_HOST, SERVER_PORT
import gui.webview_client.webview as webview

ICON_NAME = os.path.join("icons", "menubar.png")
ICON_HOVERTEXT = "trust-no-one"

BASE_SERVER_URL = "http://" + SERVER_HOST + ":" + str(SERVER_PORT)


class MainAppMenu(wx.TaskBarIcon):
    def __init__(self, app_frame):
        super(MainAppMenu, self).__init__()
        self.app_frame = app_frame  # Stored to close the app with

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
        webview.WebviewWindow(BASE_SERVER_URL + "/providers").Show()

    def on_exit(self, event):
        """
        Called with the quit item is selected.
        """
        wx.CallAfter(self.Destroy)
        self.app_frame.Close()


class SBApp(wx.App):
    def __init__(self):
        super(SBApp, self).__init__(redirect=False)

    def OnInit(self):
        frame = wx.Frame(parent=None)
        self.SetTopWindow(frame)
        MainAppMenu(frame)
        return True


def run_app():
    app = SBApp()
    app.MainLoop()
