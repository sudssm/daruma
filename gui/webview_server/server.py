import sys
import os
from flask import Flask, redirect, render_template, request, send_file
import pkg_resources
from custom_exceptions import exceptions
import gui
from managers.ProviderManager import ProviderManager
from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT


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
    """
    Serves a large version of the app logo.
    """
    icon_path = os.path.join("icons", "large.png")
    return send_file(pkg_resources.resource_filename(gui.__name__, icon_path))


@app.route('/setup')
def show_setup_page():
    """
    This page is shown on app startup when we can't automatically load an
    existing configuration.
    """
    return render_template('setup.html',
                           available_providers=ProviderManager.get_provider_classes(),
                           added_providers=global_app_state.prelaunch_providers)


@app.route('/providers')
def show_provider_status():
    """
    This page is shown as a dashboard to see the current state of providers and
    the system.
    """
    return render_template('providers.html',
                           available_providers=ProviderManager.get_provider_classes(),
                           providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


@app.route('/providers/add.html')
def show_add_provider_modal():
    """
    This page is shown in a modal dialog to allow the user to add a new
    provider.
    """
    return render_template('add_provider_modal.html',
                           available_providers=ProviderManager.get_provider_classes())


@app.route('/providers/add_failure.html')
def show_add_provider_failure_modal():
    """
    This page is shown in a modal dialog to notify the user of a failure in
    provider addition.
    """
    return render_template('add_provider_failure_modal.html')


@app.route('/providers/add/<provider_name>')
def add_provider(provider_name):
    """
    This endpoint allows the user to authorize/configure a new instance of the
    selected provider type.  If the provider is an OAuth provider, it redirects
    to the authorization page.  Otherwise, it displays the provider
    configuration page.
    """
    oauth_providers, unauth_providers = ProviderManager.get_provider_classes_by_kind()
    provider_manager = global_app_state.provider_manager
    if provider_name in oauth_providers:
        provider_class = oauth_providers[provider_name]
        oauth_url = provider_manager.start_oauth_connection(provider_class)
        return redirect(oauth_url)
    else:
        try:
            provider_class = unauth_providers[provider_name]
            return render_template("provider_configuration_modal.html",
                                   identifier=provider_name,
                                   name=provider_class.provider_name(),
                                   configuration_label=provider_class.get_configuration_label())
        except KeyError:
            return redirect("providers/add_failure.html")


@app.route('/providers/add/<provider_name>/finish')
def finish_adding_provider(provider_name):
    """
    This endpoint constructs a provider with the necessary configuration (e.g.
    login token in its query string.  Use this as the OAuth redirect URL.
    This endpoint also closes the current modal dialog window.
    """
    oauth_providers, unauth_providers = ProviderManager.get_provider_classes_by_kind()
    provider_manager = global_app_state.provider_manager
    if provider_name in oauth_providers:
        try:
            provider_class = oauth_providers[provider_name]
            new_provider = provider_manager.finish_oauth_connection(provider_class, request.url)
        except exceptions.ProviderOperationFailure:
            return redirect("providers/add_failure.html")
        else:
            global_app_state.prelaunch_providers.append(new_provider)
            return redirect("modal/close")
    else:
        try:
            provider_class = unauth_providers[provider_name]
            provider_id = request.args.get("id")
            new_provider = provider_manager.make_unauth_provider(provider_class,
                                                                 provider_id)
            global_app_state.prelaunch_providers.append(new_provider)
            return redirect("modal/close")
        except (KeyError, exceptions.ProviderOperationFailure):
            return redirect("provider/add_failure.html")


def start_ui_server(native_app, app_state):
    """
    Begins running the UI webserver.

    Args:
        native_app: A reference to the menubar app.
        app_state: An ApplicationState object
    """
    global global_app_state
    global_app_state = app_state
    app.run(host=INTERNAL_SERVER_HOST, port=INTERNAL_SERVER_PORT)
