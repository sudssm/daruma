from flask import Flask, render_template
app = Flask(__name__)

WEBVIEW_SERVER_HOST = "localhost"
WEBVIEW_SERVER_PORT = 28962  # This should be a free port


@app.route('/setup')
def show_setup_page():
    return render_template('setup.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


@app.route('/providers')
def show_provider_status():
    return render_template('providers.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


def start_ui_server():
    """
    Begins running the UI webserver.
    """
    app.run(host=WEBVIEW_SERVER_HOST, port=WEBVIEW_SERVER_PORT)
