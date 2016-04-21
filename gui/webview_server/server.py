import os
from flask import Flask, redirect, render_template, request, send_file, jsonify
import pkg_resources
from custom_exceptions import exceptions
import gui
from tools.utils import INTERNAL_SERVER_HOST, INTERNAL_SERVER_PORT, get_resource_path
from driver.Daruma import Daruma


app = Flask(__name__,
            static_folder=get_resource_path("static"),
            template_folder=get_resource_path("templates"))
global_app_state = None


#########################
# Primary GUI endpoints #
#########################


@app.route('/app_logo.png')
def download_logo():
    """
    Serves a large version of the app logo.
    """
    icon_path = os.path.join("icons", "large.png")
    return send_file(pkg_resources.resource_stream(gui.__name__, icon_path))


@app.route('/setup.html')
def show_setup_page():
    """
    This splash page is shown on app startup when we can't automatically load
    an existing configuration.
    """
    return render_template('setup.html')


@app.route('/setup_add_providers.html')
def show_setup_add_page():
    """
    This page is shown to allow users to add providers before loading or
    creating an instance.
    """
    return render_template('setup_add_providers.html',
                           available_providers=global_app_state.provider_manager.get_provider_classes())


@app.route('/providers.html')
def show_provider_status():
    """
    This page is shown as a dashboard to see the current state of providers and
    the system.
    """
    # TODO show something if we are in read only mode
    return render_template('providers.html')


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
    if new_provider.uuid in global_app_state.provider_uuids_map:
        # The provider already exists
        # TODO give a nice error
        return redirect("providers/add_failure.html")
    else:
        global_app_state.providers.append(new_provider)
        global_app_state.provider_uuids_map[new_provider.uuid] = new_provider

        # if we already have an instance, we need to reprovision
        if global_app_state.daruma is not None:
            global_app_state.needs_reprovision = True
        return redirect("modal/close")


@app.route('/load_instance')
def try_load_instance():
    """
    Attempts to load Daruma instance from active providers
    Redirects to either status or confirmation page
    """
    if len(global_app_state.providers) < 3:
        return redirect("setup_add_providers.html")

    try:
        # TODO handle extra providers
        global_app_state.daruma, extra_providers = Daruma.load(global_app_state.providers)
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


##################
# JSON endpoints #
##################


@app.route('/get_state')
def get_provider_list():
    """
    An API endpoint that returns a JSON-formatted list of active providers
    """
    instance = None
    providers = []
    overall_status = "GREEN"

    for provider in global_app_state.providers:
        provider_dict = {
            "name": provider.provider_name(),
            "identifier": provider.provider_identifier(),
            "id": provider.uid,
            "status": provider.status,
        }
        providers.append(provider_dict)

        if provider.status == "RED":
            if overall_status == "GREEN":
                overall_status = "YELLOW"
            else:
                overall_status = "RED"

    if global_app_state.daruma is not None:
        instance = {
            "status": overall_status,
            "needs_reprovision": global_app_state.needs_reprovision
        }

    return jsonify({
        'instance': instance,
        'providers': providers
    })


@app.route('/remove_provider')
def remove_provider():
    identifier = request.args.get("identifier")
    uid = request.args.get("id")

    try:
        provider = global_app_state.provider_uuids_map[(identifier, uid)]
        del global_app_state.provider_uuids_map[(identifier, uid)]
        global_app_state.providers.remove(provider)
    except KeyError:
        return ""

    # we removed a provider, should reprovision
    global_app_state.needs_reprovision = True
    return ""


@app.route('/provision_instance')
def try_provision_instance():
    """
    Attempt to provision a Daruma object given the current list of providers.
    """
    try:
        global_app_state.daruma = Daruma.provision(global_app_state.providers,
                                                   len(global_app_state.providers) - 1,
                                                   len(global_app_state.providers) - 1)
        return jsonify({"success": True})
    except exceptions.FatalOperationFailure as e:
        return jsonify({
            "success": False,
            "errors": map(lambda failure: (failure.provider.provider_name(), failure.provider.uid), e.failures)
        })


@app.route('/reprovision')
def reprovision():
    try:
        global_app_state.daruma.reprovision(global_app_state.providers, len(global_app_state.providers) - 1, len(global_app_state.providers) - 1)
    except:
        pass
    global_app_state.providers = global_app_state.daruma.get_providers()
    global_app_state.provider_uuids_map = {provider.uuid: provider for provider in global_app_state.providers}
    global_app_state.needs_reprovision = False
    return ""


@app.route('/iconstatus')
def get_icon_statuses():
    try:
        status_dict = {path: 2 for path in global_app_state.daruma.list_all_paths()}
        status_dict[""] = 2
    except AttributeError:
        status_dict = {}
    return jsonify(status_dict)


def start_ui_server(native_app, app_state):
    """
    Begins running the UI webserver.

    Args:
        native_app: A reference to the menubar app.
        app_state: An ApplicationState object
    """
    global global_app_state
    global_app_state = app_state
    global_app_state.provider_uuids_map = {provider.uuid: provider for provider in global_app_state.providers}
    app.run(host=INTERNAL_SERVER_HOST, port=INTERNAL_SERVER_PORT, debug=True, use_reloader=False)
