import socket
import sys
import os
from flask import Flask, render_template

# Change the static and template folder locations depending on whether we're
# running in an app and what the platform is.  Py2App sets the sys.frozen
# attribute, so we're just testing for that now.  For compatibility with other
# installers, inspect the value of the attribute.
if getattr(sys, "frozen", None):
    app = Flask(__name__,
                static_folder=os.path.join(os.getcwd(), "static"),
                template_folder=os.path.join(os.getcwd(), "templates"))
else:
    app = Flask(__name__)


@app.route('/providers')
def show_provider_status():
    return render_template('providers.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


class UI_Server(object):
    """
    Represents the UI server and exposes the information needed to connect to it.
    """
    _MAX_SERVER_PORT = 65535
    _INITIAL_SERVER_PORT = 49152  # A standard start of the ephemeral port range

    def __init__(self):
        self.host = "localhost"
        self.port = UI_Server._INITIAL_SERVER_PORT

    def start(self):
        """
        Begins running the UI server.

        Raises:
            socket.error: No port was available.
        """
        # Selects an ephemeral port via trial-and-error.
        # The standard technique of choosing port 0 does not apply, as flask
        # does not expose port numbers once the server is started.
        while True:
            try:
                app.run(host=self.host, port=self.port)
                break
            except socket.error:
                self.port += 1
                if self.port > UI_Server._MAX_SERVER_PORT:
                    raise
