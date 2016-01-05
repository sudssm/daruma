import exceptions
import re


class ManifestEntry:
    DELIM = ","
    TRUENAME = '[a-zA-Z0-9_\.]+'
    CODENAME = '[A-Z0-9_]{32}'
    SIZE = '[0-9]+'
    KEY = '.{32}'

    STRREGEX = '(' + TRUENAME + ')' + DELIM + '(' + CODENAME + ')' + \
        DELIM + '(' + SIZE + ')' + DELIM + '(' + KEY + ')'
    REGEX = re.compile(STRREGEX, re.DOTALL)

    # @param atributes: {"true_name": "", "code_name": "", "size": , "aes_key": }
        # true_name: string of true name
        # code_name: string of code name
        # size: decimal value of size
        # aes_key: byte rep of key
    # @param str: string representation of entry
    def __init__(self, attributes=None, str_line=None):
        if attributes is not None and str_line is None:
            self.attributes = attributes

            test_str = self.stringify()
            test_attr = self.parse(test_str)
            if (test_attr != attributes):
                raise exceptions.IllegalArgumentException
        elif str_line is not None and attributes is None:
            self.attributes = self.parse(str_line)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        return self.attributes == other.attributes

    # returns a negative integer if self < other, zero if self == other, and positive if self > other
    def __cmp__(self, other):
        return cmp(self.attributes["true_name"], other.attributes["true_name"])

    def parse(self, str_line):
        res = self.REGEX.match(str_line)
        if res is None or res.group(0) != str_line:
            raise exceptions.IllegalArgumentException
        attrs = res.groups()
        if (len(attrs) != 4):
            raise exceptions.IllegalArgumentException
        else:
            return {"true_name": attrs[0], "code_name": attrs[1],
                    "size": int(attrs[2]), "aes_key": attrs[3]}

    # TODO: note - make stringify methods __str__ so that str(manifest) works, unless you have good reason?
    # @return: string representation of entry
    def stringify(self):
        return self.attributes["true_name"] + self.DELIM + self.attributes["code_name"] + self.DELIM + \
            str(self.attributes["size"]) + self.DELIM + self.attributes["aes_key"]

class Manifest:
    NEWLINE = "\n"
    STRREGEX = "(" + ManifestEntry.TRUENAME + ManifestEntry.DELIM + ManifestEntry.CODENAME + \
        ManifestEntry.DELIM + ManifestEntry.SIZE + ManifestEntry.DELIM + ManifestEntry.KEY + \
        NEWLINE + ")"
    REGEX = re.compile(STRREGEX, re.DOTALL)

    def __init__(self, lines=None, content=None):
        # if both are none, make an empty manifest
        if lines is None and content is None:
            lines = []

        if lines is not None and content is None:
            test_content = ""
            for line in lines:
                test_content += line.stringify() + self.NEWLINE
            if lines.sort() != self.parse(test_content).sort():
                raise exceptions.IllegalArgumentException

            self.lines = lines
        elif content is not None and lines is None:
            self.lines = self.parse(content)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        return self.lines.sort() == other.lines.sort()

    def parse(self, content):
        lines = []
        str_lines = self.REGEX.findall(content)
        if "".join(str_lines) != content:
            raise exceptions.IllegalArgumentException  # any invalid text will result in failure
        for str_line in str_lines:
            lines.append(ManifestEntry(str_line=str_line[:-1]))  # remove terminating newline
        return lines

    def stringify(self):
        if len(self.lines) == 0:
            return ""
        str_lines = [line.stringify() for line in self.lines]
        # TODO: should we randomize line order with each call?
        str_manifest = self.NEWLINE.join(str_lines) + self.NEWLINE
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
    # @param: string representing the new file code name
    # @param: decimal representation of size
    # @param: byte representation of the AES key
    # @return: old code file name
    def update_manifest(self, true_name, new_code_name, size, aes_key):
        # TODO: are we rotating AES keys when we update an old file?

        # search the manifest with the provided true_name
        line = self.remove_line(true_name)
        
        attributes = {"true_name": true_name, "code_name": new_code_name,
                      "size": size, "aes_key": aes_key}
        if line:
            old_code_name = line.attributes["code_name"]
        else:
            old_code_name = None
        self.lines.append(ManifestEntry(attributes))

        # return old code_name and new manifest
        return old_code_name
