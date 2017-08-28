"""
Bifile.
"""
from hashlib import sha1

BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

class BiFile:
    """
    Represents a file for PowerBi

    :param path:
        Full path of the file.
    :type path:
        `unicode`
    :param filename:
        Filename with extension of the file.
    :type filename:
        `unicode`
    :param shared_link:
        URL to download the file.
    :type shared_link:
        `unicode`
    """

    def __init__(self, path=None, filename=None, shared_link=None):
        self.path = path
        self.filename = filename
        self.shared_link = shared_link

    def to_json(self):
        """
        Serializes the object

        :return:
            The serilized object
        :rtype:
            `dict`
        """
        return self.__dict__

    @property
    def sha1(self):
        """
        The SHA1 of the file.

        :return:
            The SHA1 value of the file.
        :rtype:
            `unicode`
        """
        filehash = sha1()
        with open(self.path, 'rb') as infile:
            while True:
                data = infile.read(BUF_SIZE)
                if not data:
                    break
                filehash.update(data)
        return filehash.hexdigest()
