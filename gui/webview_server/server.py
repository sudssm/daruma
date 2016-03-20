import socket
from flask import Flask, render_template
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
        self._host = "localhost"
        self._port = UI_Server._INITIAL_SERVER_PORT

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
                app.run(host=self._host, port=self._port)
                break
            except socket.error:
                self._port += 1
                if self._port > UI_Server._MAX_SERVER_PORT:
                    raise

    @property
    def host(self):
        return self._host

    @property
    def port(self):
        return self._port
