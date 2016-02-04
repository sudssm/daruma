import dropbox


class DropboxProvider(BaseProvider):
    def __init__(self, access_token=""):
        """
        Initialize a dropbox provider.

        Args:
            access_token: the access_token for the user. See more in GetAccessToken.py. 
        """

        self.access_token = access_token
        self.client = dropbox.client.DropboxClient(self.access_token)

    def connect(self):
        # might consider run get access token here. Only initialize provider with app information.
        pass
        
    def get(self, filename):
        f, metadata = client.get_file_and_metadata(filename)
        out = open(filename, 'wb')
        out.write(f.read())
        out.close()

    def put(self, filename, data):
        response = self.client.put_file(filename, data, overwrite=True)

    def delete(self, filename):
        self.client.file_delete(filename)

    def wipe (self):
        pass