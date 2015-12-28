import exceptions


class Manifest:
    NEWLINE = "\n"

    def __init__(self, lines=None, content=None):
        if lines is not None and content is None:
            self.lines = lines
        elif content is not None and lines is None:
            self.lines = []
            for str_line in content.split(self.NEWLINE):
                self.lines.append(ManifestEntry(str_line=str_line))
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        # TODO: want a faster runtime?
        return self.lines.sort() == other.lines.sort()

    def stringify(self):
        str_lines = [line.stringify() for line in self.lines]
        # TODO: should we randomize line order with each call?
        str_manifest = str_lines.join(self.NEWLINE)
        return str_manifest

    def ls(self):
        names = []
        for line in self.lines:
            names.append(line.attributes["true_name"])
        return names

    def get_line(self, true_name):
        for line in self.lines:
            if line.attributes["true_name"] == true_name:
                return line
        return None

    def remove_line(self, true_name):
        line = self.get_line(true_name)
        if line is not None:
            self.lines.remove(line)
            return line
        return None

    # Updates the manifest in place
    # @param: string representing the true filename
    # @param: string representing the new random filename
    # @param: decimal representation of size
    # @param: byte representation of the AES key
    # @return: old random file name
    def update_manifest(self, true_name, new_random_name, size, aes_key):
        # TODO: are we rotating AES keys when we update an old file?

        # search the manifest with the provided true_name
        line = self.remove_line(true_name)
        if line is not None:
            attributes = line.attributes
            old_random_name = attributes["random_name"]
            attributes["random_name"] = new_random_name
            attributes["size"] = size
            # TODO: update aes_key if we choose to rotate keys

            self.lines.append(ManifestEntry(attributes))  # add the updated line back in
        else:  # the file does not exist
            attributes = {"true_name": true_name, "random_name": new_random_name,
                          "size": size, "aes_key": aes_key}
            old_random_name = None
            self.lines.append(ManifestEntry(attributes))

        # return old random_name and new manifest
        return old_random_name


class ManifestEntry:
    DELIM = ","

    # @param atributes: {"true_name": "", "random_name": "", "size": , "aes_key": }
        # true_name: string of true name
        # random_name: string of random name
        # size: decimal value of size
        # aes_key: byte rep of key
    # @param str: string representation of entry
    def __init__(self, attributes=None, str_line=None):
        if attributes is not None and str_line is None:
            self.attributes = attributes
        elif str_line is not None and attributes is None:
            self.attributes = self.parse(str_line)
        else:
            raise exceptions.IllegalArgumentException

    def parse(self, str_line):
        terms = str_line.split(self.DELIM)
        if (len(terms) != 4):
            raise exceptions.IllegalArgumentException
        else:
            return {"true_name": terms[0], "random_name": terms[1],
                    "size": float(terms[2]), "aes_key": terms[3]}

    # @return: string representation of entry
    def stringify(self):
        return self.attributes["true_name"] + self.DELIM + self.attributes["random_name"] + self.DELIM + \
            str(self.attributes["size"]) + self.DELIM + self.attributes["aes_key"]
