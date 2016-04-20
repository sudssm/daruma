import onedrivesdk
from onedrivesdk.error import ErrorCode, OneDriveError
import pickle
import json
import requests
from contextlib import contextmanager
from providers.OAuthProvider import OAuthProvider
from custom_exceptions import exceptions
from tools.utils import parse_url


class OneDriveProvider(OAuthProvider):
    SCOPES = ['wl.emails', 'onedrive.readwrite', 'wl.offline_access']

    @classmethod
    def provider_identifier(cls):
        return "onedrive"

    @classmethod
    def provider_name(cls):
        return "OneDrive"

    def __init__(self, credential_manager):
        super(OneDriveProvider, self).__init__(credential_manager)
        self._app_credentials = None
        self.client = None

    @contextmanager
    def exception_handler(self):
        error_map = {
            ErrorCode.AccessDenied:         exceptions.AuthFailure,
            ErrorCode.ActivityLimitReached: exceptions.ConnectionFailure,
            ErrorCode.GeneralException:     exceptions.ProviderOperationFailure,
            ErrorCode.InvalidRange:         exceptions.ProviderOperationFailure,
            ErrorCode.InvalidRequest:       exceptions.ProviderOperationFailure,
            ErrorCode.ItemNotFound:         exceptions.ProviderOperationFailure,
            ErrorCode.Malformed:            exceptions.ProviderOperationFailure,
            ErrorCode.MalwareDetected:      exceptions.ProviderOperationFailure,
            ErrorCode.NameAlreadyExists:    exceptions.ProviderOperationFailure,
            ErrorCode.NotAllowed:           exceptions.ProviderOperationFailure,
            ErrorCode.NotSupported:         exceptions.ProviderOperationFailure,
            ErrorCode.QuotaLimitReached:    exceptions.ConnectionFailure,
            ErrorCode.ResourceModified:     exceptions.ProviderOperationFailure,
            ErrorCode.ResyncRequired:       exceptions.ProviderOperationFailure,
            ErrorCode.ServiceNotAvailable:  exceptions.ConnectionFailure,
            ErrorCode.Unauthenticated:      exceptions.AuthFailure
        }
        try:
            yield
        except OneDriveError as e:
            raise error_map.get(e.message.split()[0], exceptions.ProviderOperationFailure)(self)
        except:
            raise exceptions.ProviderOperationFailure(self)

    def start_connection(self):
        client_id = self.app_credentials['client_id']

        self.client = onedrivesdk.get_default_client(client_id=client_id, scopes=self.SCOPES)
        auth_url = self.client.auth_provider.get_auth_url(self.get_oauth_redirect_url())
        return auth_url

    def finish_connection(self, url):
        client_secret = self.app_credentials['client_secret']

        params = parse_url(url)

        with self.exception_handler():
            self.client.auth_provider.authenticate(params["code"], self.get_oauth_redirect_url(), client_secret)

        self._connect(self.client.auth_provider._session)

    def _connect(self, _session):
        # to be called with a OneDrive session object or pickle  string
        if type(_session) in [str, unicode]:
            _session = pickle.loads(_session)

        if self.client is None:
            client_id = self.app_credentials['client_id']
            self.client = onedrivesdk.get_default_client(client_id=client_id, scopes=self.SCOPES)
        self.client.auth_provider._session = _session

        # get email
        url = "https://apis.live.net/v5.0/me"
        with self.exception_handler():
            req = onedrivesdk.request_base.RequestBase(url, self.client, [])
            req.method = "GET"
            res = req.send()
            assert res.status == 200
            self.email = json.loads(res.content)["emails"]["preferred"]

        self.credential_manager.set_user_credentials(self.__class__, self.uid, pickle.dumps(_session))

    @property
    def uid(self):
        return self.email

    def _get_item(self, filename):
        return self.client.item(path=self.ROOT_DIR + "/" + filename)

    def get(self, filename):
        with self.exception_handler():
            request = self._get_item(filename).content.request()
            self.client.auth_provider.authenticate_request(request)
            response = requests.get(request.request_url, headers=request._headers)

            # create a response. This will throw appropriate errors as needed
            onedrivesdk.http_response.HttpResponse(response.status_code, response.headers, response.text)

            return ''.join(response.iter_content())

    def put(self, filename, data):
        with self.exception_handler():
            request = self._get_item(filename).content.request()
            request.append_option(onedrivesdk.options.HeaderOption("Content-Type", "application/octet-stream"))
            self.client.auth_provider.authenticate_request(request)
            self.client.http_provider.send("PUT", request._headers, request.request_url, data=data)

    def get_capacity(self):
        # TODO
        with self.exception_handler():
            drive = self.client.drive.get()
            total = drive.quota.total
            used = drive.quota.used

    def delete(self, filename):
        with self.exception_handler():
            self._get_item(filename).delete()

    def wipe(self):
        with self.exception_handler():
            try:
                self._get_item("").delete()
            except OneDriveError as e:
                # if does not exist, consider this successfully wiped
                if e.message.split()[0] != ErrorCode.ItemNotFound:
                    raise
