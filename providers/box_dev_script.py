from tools.utils import parse_url
from contextlib import contextmanager
from custom_exceptions import exceptions
from providers.OAuthProvider import OAuthProvider
from boxsdk import OAuth2, Client
from boxsdk.exception import BoxOAuthException, BoxAPIException
from StringIO import StringIO
from requests.exceptions import ReadTimeout
import json

client_id = "ic2jp8xqbhj5tyiux4mxh8yhwzivz1bh"
client_secret = "NxGsoHM4yPwDudlUUI2n97BE01TGaVOj"

oauth = OAuth2(client_id=client_id, client_secret=client_secret)
authorize_url, csrf_token = oauth.get_authorization_url("http://localhost")

redirectUrl = "http://localhost/?state=box_csrf_token_RMVtBLtE80TLUIHx&code=m9PoChb9SLw4mVCKbJ3DXOTpU9mf0zsc"

params = parse_url(url)