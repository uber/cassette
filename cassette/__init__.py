import contextlib
import logging
import os
import urllib
import urllib2
from io import StringIO

import yaml


old_urlopen = urllib2.urlopen
cassette_library = None


class CassetteLibrary(dict):

    def __init__(self, filename):
        """Create a CassetteLibrary object.

        :param str filename: filename to file holding fake response
        """

        self.filename = os.path.abspath(filename)

        if not os.path.exists(self.filename):
            return

        self.load_file()

    def add_response(self, key, response):
        """Add a new response to the mocked response.

        :param str key:
        :param addinfourl response:

        :rtype MockedResponse:
        """

        mocked = MockedResponse.from_info_url(response)
        self[key] = mocked
        self.write_to_file()

        return mocked

    def write_to_file(self):
        """Write mocked responses to file."""

        # Get dict representation of MockedResponse objects
        def is_lambda(v):
            return isinstance(v, type(lambda: None)) and v.__name__ == '<lambda>'

        data = {}
        for k, v in self.items():
            if hasattr(k, 'get_method') and is_lambda(k.get_method):
                k.get_method = k.get_method()

            data[k] = v.as_dict()

        with open(self.filename, "w+") as f:
            yaml.dump(data, f)

    def load_file(self):
        """Load MockedResponses from YAML file."""

        with open(self.filename) as f:
            data = yaml.load(f)

        self.update({k: MockedResponse.from_dict(v) for k, v in data.items()})


class MockedResponse(urllib.addinfourl):
    """Subclass of this crazy addinfourl object that is defined in urllib."""

    @classmethod
    def create_fake(cls, url, headers, code, content):
        """Create a fake Response.

        This class method is needed so that we don't have to change the default
        constructor signature.
        """

        fp = StringIO(unicode(content))

        # In urllib, constructor defined as
        # __init__(self, fp, headers, url, code=None)
        obj = cls(fp, headers, url, code)
        obj.content = content
        obj.read = fp.read

        return obj

    @classmethod
    def from_info_url(cls, info_url):
        """Create from an info_url object (returned by urllib2.urlopen)."""
        return cls.create_fake(info_url.url, info_url.headers, info_url.code,
                               info_url.read(10000000))

    @classmethod
    def from_dict(cls, data):
        """Create from dict representation.

        :param dict data:
        """
        return cls.create_fake(**data)

    def as_dict(self):
        """Return dict representation."""
        return {
            "content": self.content,
            "headers": self.headers,
            "url": self.url,
            "code": self.code
        }


def cassette_urlopen(url, data=None, timeout=None):
    """Fake urlopen function that will return from a file if a response exists."""

    key = url
    if data:
        key += str(data)

    if not key in cassette_library:
        # We do not have the response, let's do a real HTTP request
        params = [url, data]
        if timeout:
            params.append(timeout)

        logging.debug("'%s' not in library, making HTTP request." % key)

        response = old_urlopen(*params)
        # And add it to the library
        response = cassette_library.add_response(key, response)

    else:
        response = cassette_library[key]

    return response


def patch():
    """Replace standard library methods."""
    urllib2.urlopen = cassette_urlopen


def unpatch():
    """Unpatch."""
    urllib2.urlopen = old_urlopen


def insert(filename):
    """Setup cassette.

    :param filename: path to .yaml where requests and responses will be stored.
    """
    global cassette_library

    patch()
    cassette_library = CassetteLibrary(filename)


def eject():
    """Remove cassette, unpatching HTTP requests."""
    unpatch()


@contextlib.contextmanager
def play(filename):
    """Use cassette."""
    insert(filename)
    yield
    eject()
