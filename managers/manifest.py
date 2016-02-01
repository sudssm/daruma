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

    def __init__(self, attributes=None, str_line=None):
        """
        Args:
            attributes={"true_name": "", "code_name": "", "size": , "aes_key": }
                true_name: string of true name
                code_name: string of code name
                size: decimal value of size
                aes_key: byte rep of aes_key
        or
            str_line="string representation of a manifest entry"
        Raises:
            IllegalArgumentException if zero or two arguments are specified
        """
        if attributes is not None and str_line is None:
            self.attributes = self.assign_attributes(attributes)
        elif str_line is not None and attributes is None:
            self.attributes = self.parse(str_line)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        """
        ManifestEntries are considered equal if the dictionary representations
        of their attributes are equal
        """
        return self.attributes == other.attributes

    def __str__(self):
        """
        Returns:
            string representation of a ManifestEntry
        """
        return self.attributes["true_name"] + self.DELIM + self.attributes["code_name"] + \
            self.DELIM + str(self.attributes["size"]) + self.DELIM + self.attributes["aes_key"]

    def __cmp__(self, other):
        """
        Defines comparison for ManifestEntries to allow for sorting.
        Uses lexicographical ordering on the true file name.
        Returns:
            a negative integer if self < other, zero if self == other, and positive if self > other
        """
        return cmp(self.attributes["true_name"], other.attributes["true_name"])

    def verify_truename(self, truename):
        """
        Args:
            string of true name for verification
        Returns:
            true if name is valid based on the defined regex, false if not
        """
        match = self.TRUENAME.match(truename)
        return match and match.group(0) == truename

    def verify_codename(self, codename):
        """
        Args:
            string of code name for verification
        Returns:
            true if name is valid based on the defined regex, false if not
        """
        match = self.CODENAME.match(codename)
        return match and match.group(0) == codename

    def verify_size(self, size):
        """
        Args:
            decimal of size for verification
        Returns:
            true if size is valid based on the defined regex, false if not
        """
        match = self.SIZE.match(size)
        return match and match.group(0) == size

    def verify_aeskey(self, aeskey):
        """
        Args:
            byte representation of the AES key for verification
        Returns:
            true if AES key is valid based on the defined regex, false if not
        """
        match = self.KEY.match(aeskey)
        return match and match.group(0) == aeskey

    def verify_attributes(self, attributes):
        """
        Args:
            dictionary of ManifestEntry attributes
        Returns:
            true if all attributes are verified, false otherwise
        """
        return self.verify_truename(attributes["true_name"]) and self.verify_codename(attributes["code_name"]) and \
            self.verify_size(str(attributes["size"])) and self.verify_aeskey(attributes["aes_key"])

    def assign_attributes(self, attributes):
        """
        Args:
            dictionary of ManifestEntry attributes
        Returns:
            attributes if they have been verified
        Raises:
            ParseException if attributes are not verified
        """
        if (self.verify_attributes(attributes)):
            return attributes
        else:
            raise exceptions.ParseException

    def parse(self, str_line):
        """
        Args:
            string representation of a ManifestEntry
        Returns:
            dictionary of ManifestEntry attributes if the line can be parsed
        Raises:
            ParseException if the line cannot be parsed
        """
        res = self.REGEX.match(str_line)
        if res is None or res.group(0) != str_line:
            raise exceptions.ParseException
        attrs = res.groups()
        if len(attrs) != 4:
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
        """
        Args:
            no args, creates an empty Manifest
        or
            lines=[list of ManifestEntry objects]
        or
            content="string representation of the Manifest content"
        Raises:
            IllegalArgumentException if two arguments are specified
        """
        if lines is None and content is None:
            self.lines = []
        elif lines is not None and content is None:
            self.lines = lines  # the ManifestEntries have already been validated
        elif content is not None and lines is None:
            self.lines = self.parse(content)
        else:
            raise exceptions.IllegalArgumentException

    def __eq__(self, other):
        """
        Manifests are equal if they contain the same lines
        Need to sort here to get desired list equality
        """
        return other is not None and self.lines.sort() == other.lines.sort()

    def __str__(self):
        """
        Returns:
            string representation of a Manifest
        """
        if len(self.lines) == 0:
            return ""
        str_lines = [str(line) for line in self.lines]

        # TODO: should we randomize line order with each call?
        str_manifest = self.NEWLINE.join(str_lines) + self.NEWLINE
        return str_manifest

    def parse(self, content):
        """
        Args:
            string representation of a Manifest
        Returns:
            list of ManifestEntry attributes
        Raises:
            ParseException if the content cannot be parsed
        """
        lines = []
        tup_lines = self.REGEX.findall(content)
        reconstruction = [tup_line[0] + tup_line[1] for tup_line in tup_lines]
        if "".join(reconstruction) != content:
            raise exceptions.ParseException  # any invalid text will result in failure
        for tup_line in tup_lines:
            lines.append(ManifestEntry(str_line=tup_line[0]))  # remove terminating newline
        return lines

    def ls(self):
        """
        Returns:
            list of true names of files in the manifest
        """
        names = []
        for line in self.lines:
            names.append(line.attributes["true_name"])
        return names

    def get_line(self, true_name):
        """
        Args:
            true name of the file to be searched for
        Returns:
            dictionary of attributes associated with the file if it is found
        Raises:
            FileNotFound if file is not found
        """
        for line in self.lines:
            if line.attributes["true_name"] == true_name:
                return line.attributes
        raise exceptions.FileNotFound

    def remove_line(self, true_name):
        """
        Args:
            true name of the file to be searched for and removed
        Returns:
            dictionary of attributes associated with the file if it is found
        Raises:
            FileNotFound if file is not found
        """
        for line in self.lines:
            if line.attributes["true_name"] == true_name:
                attributes = line.attributes
                self.lines.remove(line)
                return attributes
        raise exceptions.FileNotFound

    def update_manifest(self, true_name, new_code_name, size, aes_key):
        """
        Updates the manifest in place by either replacing the line
        specified by the given true file name or by creating a new line
        with the given parameters

        Args:
            true_name: string representing the true filename
            new_code_name: string representing the new file code name
            size: decimal representation of size
            aes_key: byte representation of the AES key
        Returns:
            old code file name (None if creating a new line)
        """

        # TODO: are we rotating AES keys when we update an old file?
        try:
            line = self.remove_line(true_name)
            old_code_name = line["code_name"]
        except exceptions.FileNotFound:
            old_code_name = None

        attributes = {"true_name": true_name, "code_name": new_code_name,
                      "size": size, "aes_key": aes_key}

        self.lines.append(ManifestEntry(attributes))

        return old_code_name
