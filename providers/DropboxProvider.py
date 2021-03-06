import dropbox
import urllib3
from tools.utils import parse_url
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.OAuthProvider import OAuthProvider
import io


class DropboxProvider(OAuthProvider):
    @classmethod
    def provider_identifier(cls):
        return "dropbox"

    @classmethod
    def provider_name(cls):
        return "Dropbox"

    def __init__(self, credential_manager):
        super(DropboxProvider, self).__init__(credential_manager)

    @contextmanager
    def exception_handler(self):
        try:
            yield

        except (dropbox.oauth.NotApprovedException, dropbox.oauth.BadStateException,
                dropbox.oauth.CsrfException, dropbox.oauth.BadRequestException):
            raise exceptions.AuthFailure(self)

        except dropbox.oauth.ProviderException:
            raise exceptions.ProviderOperationFailure(self)

        except urllib3.exceptions.MaxRetryError:
            raise exceptions.ConnectionFailure(self)

        except dropbox.rest.ErrorResponse as e:
            if e.status in [401, 400]:
                raise exceptions.AuthFailure(self)
            raise exceptions.ProviderOperationFailure(self)

        except Exception:
            raise exceptions.ProviderOperationFailure(self)

    def start_connection(self):
        credentials = self.app_credentials
        app_key, app_secret = credentials["app_key"], credentials["app_secret"]

        with self.exception_handler():
            self.flow = dropbox.client.DropboxOAuth2Flow(app_key, app_secret, self.get_oauth_redirect_url(), {}, "dropbox-auth-csrf-token")
            authorize_url = self.flow.start()

        return authorize_url

    def finish_connection(self, url):
        params = parse_url(url)

        # get auth_token
        with self.exception_handler():
            auth_token, _, _ = self.flow.finish(params)

        self._connect(auth_token)

    def _connect(self, auth_token):
        with self.exception_handler():
            self.client = dropbox.client.DropboxClient(auth_token)
            self.dropbox = dropbox.Dropbox(auth_token)
            self.email = self.client.account_info()['email']
        self.credential_manager.set_user_credentials(self.__class__, self.uid, auth_token)

    @property
    def uid(self):
        return self.email

    def get(self, filename):
        with self.exception_handler():
            with self.client.get_file(filename) as f:
                return f.read()

    def put(self, filename, data):
        with self.exception_handler():
            max_chunk_size = 157286400  # 150 mb
            size = len(data)
            if size < max_chunk_size:
                self.client.put_file(filename, data, overwrite=True)
            else:
                fh = io.BytesIO(data)
                uploader = self.client.get_chunked_uploader(fh, size)
                while uploader.offset < size:
                    uploader.upload_chunked()
                uploader.finish(filename)

    def get_capacity(self):
        with self.exception_handler():
            space_usage = self.dropbox.users_get_space_usage()
            used_space = space_usage.used
            total_allocated_space = space_usage.allocation.get_individual().allocated

            return used_space, total_allocated_space

    def delete(self, filename):
        with self.exception_handler():
            self.client.file_delete(filename)

    def wipe(self):
        with self.exception_handler():
            has_more = True
            while has_more:
                delta = self.client.delta()
                has_more = delta['has_more']
                entries = delta['entries']
                for e in entries:
                    self.delete(e[0])
