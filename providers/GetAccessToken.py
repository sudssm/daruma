import dropbox

# From Dropbox developer site. 
APP_KEY = "tzrbhn0sah5jvd3"
APP_SECRET = "pv5a53ofk9qlxfi"

def get_dropbox_token():
	"""
	Get user access token using APP_KEY and APP_SECRET
	"""

	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY,APP_SECRET)
	authorize_url = flow.start()
	code = raw_input("Enter the authorization code here: ").strip()
	access_token, user_id = flow.finish(code)

	return access_token

