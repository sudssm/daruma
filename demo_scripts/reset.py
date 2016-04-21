import sys, os
from shutil import copyfile
from demo_provider.client.TestServerProvider import TestServerProvider
from managers.ProviderManager import ProviderManager
from managers.CredentialManager import CredentialManager
from custom_exceptions import exceptions

def main(args):
   provider_manager = ProviderManager()
   cm = CredentialManager()
   cm.load()

   providers, errors = provider_manager.load_all_providers_from_credentials()

   for provider in providers:
      try:
         provider.wipe()
      except Exception:
         print "failed to wipe provider: " + provider.provider_name()

   behavior = args[0]
   cm.clear_user_credentials(provider_class=None, account_identifier=None)  # clear the file

   if behavior == "setup":
      # copy in default credentials (Dropbox, GoogleDrive, OneDrive)
      default_credentials = os.path.join(cm.config_dir, "default_credentials.json")
      current_credentials = os.path.join(cm.config_dir, "user_credentials.json")
      try:
         copyfile(default_credentials, current_credentials)
      except IOError:
         print "credential reset to setup state failed, see default_credentials.json"

      if len(args) == 2:  # write credentials for the demo server
         cm.load()  # reload the credential manager with updated store

         ip_block = args[1]
         url = ''.join("http://158.130.104." + ip_block + ":5000")
         demo_server = TestServerProvider(cm)

         try: 
            demo_server.connect(url)
         except exceptions.ConnectionFailure:
            print "please start a demo server at: " + url

if __name__ == "__main__":
   """
   empty: load in empty user credentials
   setup <id_block>:
      if id_block is not specified, it loads with default credentials for OneDrive, GoogleDrive, Dropbox
      if an id_block is specified, it also loads credentials for a DemoServer
   """
   main(sys.argv[1:])