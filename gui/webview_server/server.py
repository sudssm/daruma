import sys
import os
from flask import Flask, redirect, render_template, request, send_file, jsonify
import pkg_resources
from custom_exceptions import exceptions
import gui
from managers.ProviderManager import ProviderManager
from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT
from driver.SecretBox import SecretBox


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


@app.route('/setup.html')
def show_setup_page():
    """
    This page is shown on app startup when we can't automatically load an
    existing configuration.
    """
    return render_template('setup.html')


@app.route('/setup_add_providers.html')
def show_setup_add_page():
    """
    This page is shown on app to add providers before loading or creating an instance
    """
    return render_template('setup_add_providers.html', available_providers=global_app_state.provider_manager.get_provider_classes())


@app.route('/providers.html')
def show_provider_status():
    """
    This page is shown as a dashboard to see the current state of providers and
    the system.
    """
    # TODO show something if we are in read only mode
    return render_template('providers.html',
                           available_providers=global_app_state.provider_manager.get_provider_classes(),
                           providers=["AliceBox", "BobBox", "EveBox", "MalloryBox", "SillyBox"])


@app.route('/providers/add.html')
def show_add_provider_modal():
    """
    This page is shown in a modal dialog to allow the user to add a new
    provider.
    """
    return render_template('add_provider_modal.html',
                           available_providers=global_app_state.provider_manager.get_provider_classes())


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
    oauth_providers, unauth_providers = global_app_state.provider_manager.get_provider_classes_by_kind()
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
    oauth_providers, unauth_providers = global_app_state.provider_manager.get_provider_classes_by_kind()
    provider_manager = global_app_state.provider_manager
    if provider_name in oauth_providers:
        try:
            provider_class = oauth_providers[provider_name]
            new_provider = provider_manager.finish_oauth_connection(provider_class, request.url)
        except exceptions.ProviderOperationFailure:
            return redirect("providers/add_failure.html")
    else:
        try:
            provider_class = unauth_providers[provider_name]
            provider_id = request.args.get("id")
            new_provider = provider_manager.make_unauth_provider(provider_class, provider_id)
        except (KeyError, exceptions.ProviderOperationFailure):
            return redirect("providers/add_failure.html")

    # new_provider has been set
    if new_provider.provider_name() in global_app_state.provider_uuids:
        # TODO give a nice error
        return redirect("providers/add_failure.html")
    else:
        global_app_state.providers.append(new_provider)
        global_app_state.provider_uuids.append(new_provider.provider_name())
        return redirect("modal/close")


@app.route('/load_instance')
def try_load_instance():
    """
    Attempts to load secretbox instance from active providers
    Redirects to either status or confirmation page
    """
    if len(global_app_state.providers) < 3:
        return redirect("setup_add_providers.html")

    try:
        global_app_state.secretbox = SecretBox.load(global_app_state.providers)
        return redirect("providers.html")
    except exceptions.FatalOperationFailure:
        return redirect("modal/show/confirm_provision")


@app.route('/confirm_provision')
def confirm_provision():
    """
    Shows a confirmation before provisioning.
    Should be opened in a modal
    """
    return render_template('confirm_provision_modal.html')


@app.route('/provision_instance')
def try_provision_instance():
    """
    Attempt to provision a modal given the current list of providers.
    """
    try:
        global_app_state.secretbox = SecretBox.provision(global_app_state.providers,
                                                         len(global_app_state.providers) - 1,
                                                         len(global_app_state.providers) - 1)
        return jsonify({"success": True})
    except exceptions.FatalOperationFailure as e:
        return jsonify({
            "success": False,
            "errors": map(lambda failure: (failure.provider.provider_name(), failure.provider.provider_uid), e.failures)
        })

##################
# JSON endpoints #
##################


@app.route('/provider_list')
def get_provider_list():
    """
    An API endpoint that returns a JSON-formatted list of active providers
    """
    # TODO update for not prelaunch
    return jsonify({
        'loaded': global_app_state.secretbox is not None,
        'providers': global_app_state.provider_uuids
    })


def start_ui_server(native_app, app_state):
    """
    Begins running the UI webserver.

    Args:
        native_app: A reference to the menubar app.
        app_state: An ApplicationState object
    """
    global global_app_state
    global_app_state = app_state
    global_app_state.provider_uuids = map(lambda provider: (provider.provider_name(), provider.uid), global_app_state.providers)
    app.run(host=INTERNAL_SERVER_HOST, port=INTERNAL_SERVER_PORT, debug=True, use_reloader=False)
