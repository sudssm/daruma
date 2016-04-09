import sys
import os
from flask import Flask, render_template, send_file
import pkg_resources
import gui


WEBVIEW_SERVER_HOST = "localhost"
WEBVIEW_SERVER_PORT = 28962  # This should be a free port

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
global_app_state = None


@app.route('/app_logo.png')
def download_logo():
    icon_path = os.path.join("icons", "large.png")
    return send_file(pkg_resources.resource_filename(gui.__name__, icon_path))


@app.route('/setup')
def show_setup_page():
    return render_template('setup.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


@app.route('/providers')
def show_provider_status():
    return render_template('providers.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


def start_ui_server(native_app, app_state):
    """
    Begins running the UI webserver.

    Args:
        native_app: A reference to the menubar app.
        app_state: An ApplicationState object
    """
    global global_app_state
    global_app_state = app_state
    app.run(host=WEBVIEW_SERVER_HOST, port=WEBVIEW_SERVER_PORT)
