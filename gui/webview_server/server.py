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

WEBVIEW_SERVER_HOST = "localhost"
WEBVIEW_SERVER_PORT = 28962  # This should be a free port


@app.route('/providers')
def show_provider_status():
    return render_template('providers.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


def start_ui_server():
    """
    Begins running the UI webserver.
    """
    app.run(host=WEBVIEW_SERVER_HOST, port=WEBVIEW_SERVER_PORT)
