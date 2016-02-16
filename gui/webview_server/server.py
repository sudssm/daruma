from flask import Flask, render_template
app = Flask(__name__)

SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5000


@app.route('/providers')
def show_provider_status():
    return render_template('providers.html', providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


def start_ui_server():
    app.run(host=SERVER_HOST, port=SERVER_PORT)
