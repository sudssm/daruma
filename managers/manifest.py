from custom_exceptions import exceptions
import re


class ManifestEntry:
    DELIM = ","
    TRUENAME = re.compile('[a-zA-Z0-9_\.]+')
    CODENAME = re.compile('[A-Z0-9]{32}')
    SIZE = re.compile('[0-9]+')
    KEY = re.compile('.{32}', re.DOTALL)

    STRREGEX = '(' + TRUENAME.pattern + ')' + DELIM + '(' + CODENAME.pattern + ')' + \
        DELIM + '(' + SIZE.pattern + ')' + DELIM + '(' + KEY.pattern + ')'
    REGEX = re.compile(STRREGEX, re.DOTALL)

    # @param atributes: {"true_name": "", "code_name": "", "size": , "aes_key": }
        # true_name: string of true name
        # code_name: string of code name
        # size: decimal value of size
        # aes_key: byte rep of key
    # @param str: string representation of entry
    def __init__(self, attributes=None, str_line=None):
        if attributes is not None and str_line is None:
            self.attributes = self.assign_attributes(attributes)
        elif str_line is not None and attributes is None:
            self.attributes = self.parse(str_line)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        return self.attributes == other.attributes

    def __str__(self):
        return self.attributes["true_name"] + self.DELIM + self.attributes["code_name"] + \
            self.DELIM + str(self.attributes["size"]) + self.DELIM + self.attributes["aes_key"]

    # returns a negative integer if self < other, zero if self == other, and positive if self > other
    def __cmp__(self, other):
        return cmp(self.attributes["true_name"], other.attributes["true_name"])

    def verify_truename(self, truename):
        match = self.TRUENAME.match(truename)
        return match and match.group(0) == truename

    def verify_codename(self, codename):
        match = self.CODENAME.match(codename)
        return match and match.group(0) == codename

    def verify_size(self, size):
        match = self.SIZE.match(size)
        return match and match.group(0) == size

    def verify_aeskey(self, aeskey):
        match = self.KEY.match(aeskey)
        return match and match.group(0) == aeskey

    def verify_attributes(self, attributes):
        return self.verify_truename(attributes["true_name"]) and self.verify_codename(attributes["code_name"]) and \
            self.verify_size(str(attributes["size"])) and self.verify_aeskey(attributes["aes_key"])

    def assign_attributes(self, attributes):
        if (self.verify_attributes(attributes)):
            return attributes
        else:
            raise exceptions.ParseException

    def parse(self, str_line):
        res = self.REGEX.match(str_line)
        if res is None or res.group(0) != str_line:
            raise exceptions.ParseException
        attrs = res.groups()
        if (len(attrs) != 4):
            raise exceptions.ParseException
        else:
            return {"true_name": attrs[0], "code_name": attrs[1],
                    "size": int(attrs[2]), "aes_key": attrs[3]}


class Manifest:
    # TODO: need to add a first line for k
    NEWLINE = "\n"
    STRREGEX = "(" + ManifestEntry.TRUENAME.pattern + ManifestEntry.DELIM + ManifestEntry.CODENAME.pattern + \
        ManifestEntry.DELIM + ManifestEntry.SIZE.pattern + ManifestEntry.DELIM + ManifestEntry.KEY.pattern + \
        ")" + "(" + NEWLINE + ")"
    REGEX = re.compile(STRREGEX, re.DOTALL)

    def __init__(self, lines=None, content=None):
        # if both are none, make an empty manifest
        if lines is None and content is None:
            self.lines = []
        elif lines is not None and content is None:
            self.lines = lines  # the ManifestEntries have already been validated
        elif content is not None and lines is None:
            self.lines = self.parse(content)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        return other is not None and self.lines.sort() == other.lines.sort()

    def __str__(self):
        if len(self.lines) == 0:
            return ""
        str_lines = [str(line) for line in self.lines]

        # TODO: should we randomize line order with each call?
        str_manifest = self.NEWLINE.join(str_lines) + self.NEWLINE
        return str_manifest

    def parse(self, content):
        lines = []
        tup_lines = self.REGEX.findall(content)
        reconstruction = [tup_line[0] + tup_line[1] for tup_line in tup_lines]
        if "".join(reconstruction) != content:
            raise exceptions.ParseException  # any invalid text will result in failure
        for tup_line in tup_lines:
            lines.append(ManifestEntry(str_line=tup_line[0]))  # remove terminating newline
        return lines

    def ls(self):
        names = []
        for line in self.lines:
            names.append(line.attributes["true_name"])
        return names

    def get_line(self, true_name):
        for line in self.lines:
            if line.attributes["true_name"] == true_name:
                return line.attributes
        raise exceptions.FileNotFound

    def remove_line(self, true_name):
        for line in self.lines:
            if line.attributes["true_name"] == true_name:
                attributes = line.attributes
                self.lines.remove(line)
                return attributes
        raise exceptions.FileNotFound

    # Updates the manifest in place
    # @param: string representing the true filename
    # @param: string representing the new file code name
    # @param: decimal representation of size
    # @param: byte representation of the AES key
    # @return: old code file name
    def update_manifest(self, true_name, new_code_name, size, aes_key):
        # TODO: are we rotating AES keys when we update an old file?

        # search the manifest with the provided true_name
        try:
            line = self.remove_line(true_name)
            old_code_name = line["code_name"]
        except exceptions.FileNotFound:
            old_code_name = None

        attributes = {"true_name": true_name, "code_name": new_code_name,
                      "size": size, "aes_key": aes_key}

        self.lines.append(ManifestEntry(attributes))

        # return old code_name
        return old_code_name
