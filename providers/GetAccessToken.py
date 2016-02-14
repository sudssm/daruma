import dropbox

# From Dropbox developer site. 
APP_KEY = "btmom5enals52c3"
APP_SECRET = "dl9yxq1331z9z81"

def get_dropbox_token():
	"""
	Get user access token using APP_KEY and APP_SECRET
	"""

	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(APP_KEY,APP_SECRET)
	authorize_url = flow.start()

	# go to this link to enable app
	print "Go to this link : %s" % authorize_url

	code = raw_input("Enter the authorization code here: ").strip()
	access_token, user_id = flow.finish(code)

	return access_token


