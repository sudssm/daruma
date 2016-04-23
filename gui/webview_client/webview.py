import wx
import wx.html2 as webview


class WebviewWindow(wx.Dialog):
    def __init__(self, url=None, size=(700, 800)):
        """
        Constructs a new webview window to give the illusion of a native
        window.  In particular, this view doesn't have "back" functionality and
        displays the webpage title as its own title.

        Args:
            url: Optionally indicates the initial URL to load.
            size: A (width, height) tuple indicating the desired window size in
                  pixels.  Defaults to 700x700.
        """
        super(WebviewWindow, self).__init__(parent=None)
        self.SetSize(size)
        self.browser = webview.WebView.New(self)
        self.Bind(webview.EVT_WEBVIEW_TITLE_CHANGED, self._on_refresh_title, self.browser)

        # webview settings:
        self.browser.EnableHistory(False)

        if url:
            self.browser.LoadURL(url)

    def _on_refresh_title(self, event):
        new_title = self.browser.GetCurrentTitle()
        self.SetTitle(new_title)


class WebviewModal(wx.Dialog):
    def __init__(self, parent, url=None, size=(700, 700)):
        """
        Constructs a new webview window to give the illusion of a native
        window.  In particular, this view doesn't have "back" functionality and
        displays the webpage title as its own title.

        This class is similar to the WebviewWindow class, with the addition of a
        cancel button on the bottom for use in modal dialogs.

        Args:
            parent: The parent pane that this is a modal for.
            url: Optionally indicates the initial URL to load.
            size: A (width, height) tuple indicating the desired modal size in
                  pixels.  Defaults to 700x700.
        """
        super(WebviewModal, self).__init__(parent=parent)

        sizer = wx.BoxSizer(wx.VERTICAL)

        browser = webview.WebView.New(self)
        browser.EnableHistory(False)
        if url:
            browser.LoadURL(url)
        sizer.Add(browser, 1, wx.EXPAND)

        btnsizer = wx.StdDialogButtonSizer()

        btn = wx.Button(self, wx.ID_CANCEL)
        btnsizer.AddButton(btn)
        btnsizer.Realize()

        sizer.Add(btnsizer)

        self.SetSizer(sizer)
        self.SetSize(size)
