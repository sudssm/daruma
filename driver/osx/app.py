import rumps


class StatusBarApp(rumps.App):
    @rumps.clicked("Preferences")
    def prefs(self, _):
        rumps.alert("TODO")

if __name__ == "__main__":
    StatusBarApp("SecretBox").run()
