from providers.LocalFilesystemProvider import LocalFilesystemProvider
from driver.SecretBox import SecretBox


providers = [LocalFilesystemProvider("local_provider_storage/" + str(i)) for i in xrange(5)]
SB = SecretBox(providers, 3, 3)
SB.provision()
SB.put("testfile", "testdata")
SB.put("anothertestfile", "moredata")
print SB.get("testfile")
SB.put("testfile", "newdata")
raw_input("feel free to corrupt some files now (k=3,n=5)")

# new connection
SB = SecretBox(providers, 3, 3)
SB.start()
print SB.ls()
print SB.get("testfile")
print SB.get("anothertestfile")
SB.delete("testfile")
print SB.ls()
