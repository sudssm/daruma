import wx
import wx.html2 as webview


class WebviewWindow(wx.Dialog):
    def __init__(self, url=None):
        """
        Constructs a new webview window.  This window disables the history but
        displays the webpage title as its own title.

        Args:
            url: Optionally indicates the initial URL to load.
        """
        super(WebviewWindow, self).__init__(parent=None)
        self.SetSize((700, 700))
        self.browser = webview.WebView.New(self)
        self.Bind(webview.EVT_WEBVIEW_TITLE_CHANGED, self._on_refresh_title, self.browser)

        # webview settings:
        self.browser.EnableHistory(False)

        if url:
            self.load(url)

    def _on_refresh_title(self, event):
        new_title = self.browser.GetCurrentTitle()
        self.SetTitle(new_title)

    def load(self, url):
        """
        Loads the specified URL.
        """
        self.browser.LoadURL(url)
