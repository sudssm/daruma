import dropbox
from cStringIO import StringIO
# from custom_exceptions import exceptions
from BaseProvider import BaseProvider

# From Dropbox developer site. 
DBOX_APP_KEY = "btmom5enals52c3"
DBOX_APP_SECRET = "dl9yxq1331z9z81"
ACCESS_TOKEN = "oosk9iu5HYAAAAAAAAAADgeXRX5LJWEXV6_6GlUp6L3CWM2PgkpY2nHu99TvZDM2"

def get_access_token():
    """
    Get user access token using APP_KEY and APP_SECRET
    """

    flow = dropbox.client.DropboxOAuth2FlowNoRedirect(DBOX_APP_KEY,DBOX_APP_SECRET)
    authorize_url = flow.start()

    # go to this link to enable app
    print "Go to this link : %s" % authorize_url

    code = raw_input("Enter the authorization code here: ").strip()
    access_token, user_id = flow.finish(code)

    return access_token


class DropboxProvider(BaseProvider):
    def __init__(self, access_token=ACCESS_TOKEN):
        """
        Initialize a dropbox provider.

        Args:
            access_token: the access_token for the user. See more in GetAccessToken.py. 
        """

        self.access_token = access_token
        self.client = dropbox.client.DropboxClient(self.access_token)

    def connect(self):
        # use account info to check connection 
        try:
            account_info = self.client.account_info()
        except Exception as E:
            # Error handling
            raise Exception(E.error_msg)

    def get(self, filename):
        try:
            f, metadata = client.get_file_and_metadata(filename)
            return f.read()
        except Exception as E:
            # Error handling
            raise Exception(E.error_msg)

    def put(self, filename, data):
        try:
            f = StringIO(data)
            response = self.client.put_file(filename, f, overwrite=True)
            print "uploaded:", response
        except Exception as E:
            # Error handling
            raise Exception(E.error_msg)

    def delete(self, filename):
        try:
            self.client.file_delete(filename)
        except Exception as E:
            # Error handling
            raise Exception(E.error_msg)

    def wipe (self):
        try:
            entries = self.client.delta()['entries']
            for e in entries:
                self.client.file_delete(e[0])
        except Exception as E:
            # Error handling
            raise Exception(E.error_msg)




