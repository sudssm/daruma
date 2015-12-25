delim = '\t'
newline = '\n'


# @param: string representing the manifest
# @parem: list of strings (true file names)
def get_file_list(manifest):
    # TODO: this method assumes manifest format of
    # [true file name]\t[random file name]\t[encryption key]\n
    names = []
    for line in manifest.split(newline)[:-1]:
        names.append(line.split(delim)[0])
    return names


# @param: string representing the manifest
# @param: string representing the random filename
# @return: tuple - (<file found?>, string representing the true filename)
def get_true_name(manifest, random_name):
    # TODO: might end up having this get the names for all slices -
    # we still have to figure out how those are being handled
    pass


# @param: string representing the manifest
# @param: string representing the true filename
# @return: tuple - (<file found?>, string representing the random filename)
def get_rand_name(manifest, true_name):
    # TODO: might end up having this get the names for all slices -
    # we still have to figure out how those are being handled
    pass


# @return: string
def new_rand_name():
    # generate a new random name of a fixed size
    pass


# @param: string representing the random filename
# @param: string representing the file contents
# @return: list of tuples - (slice_name, slice)
def slice_file(random_name, file):
    # TODO: we need to discuss best way to do this /
    # how we want to do this for MVP
    pass


# @param: string representing the true filename
# @param: string representing the random filename
# @param: byte representation of the AES key
def manifest_line(true_name, random_name, aes_key):
    return true_name + delim + random_name + delim + aes_key + newline


# @param: string representing the manifest
# @param: string representing the true filename
# @param: string representing the new random filename
# @param: byte representation of the AES key
# @return: tuple - (<old file name>, <new manifest contents>)
def update_manifest(manifest, true_name, new_random_name, aes_key):
    # TODO: are we rotating AES keys when we update an old file?

    # search the manifest with the provided true_name
    for line in manifest.split(newline)[:-1]:
        vals = line.split(delim)
        if (true_name == vals[0]):
            old_random_name = vals[1]
            index = manifest.index(true_name + delim) + len(true_name + delim)  # start of random name
            # TODO: do we update the AES key?
            new_manifest = manifest[:index] + new_random_name + manifest[index + len(new_random_name):]  # TODO: this assumes all random names are the same size
            # return old random_name and new manifest
            return (old_random_name, new_manifest)
    # the file does not exist
    new_manifest = manifest + manifest_line(true_name, new_random_name, aes_key)
    return (None, new_manifest)


# @parem: list of the contents of all manifests
# @return: agreed upon version number
def establish_version(manifests):
    # TODO: Michelle needs to learn more about quorum protocol
    # called in the case where we lose our cache
    # TODO: verifying and updating the version probably don't require helper methods
    pass
