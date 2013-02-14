from __future__ import absolute_import
import os
import urllib2

import yaml

from cassette.http_response import MockedHTTPResponse
from cassette.addinfourl import MockedAddInfoURL

old_urlopen = urllib2.urlopen


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
        """Add a new response to the mocked response."""

        # Choose the class based on the response class
        if hasattr(response, "getheaders"):
            # It's an httplib.HTTPResponse
            mock_response_class = MockedHTTPResponse

        else:
            mock_response_class = MockedAddInfoURL

        mocked = mock_response_class.from_response(response)
        self[key] = mocked
        self.write_to_file()

        return mocked

    def write_to_file(self):
        """Write mocked responses to file."""

        data = {k: v.to_dict() for k, v in self.items()}
        with open(self.filename, "w+") as f:
            yaml.dump(data, f)

    def load_file(self):
        """Load MockedResponses from YAML file."""

        with open(self.filename) as f:
            data = yaml.load(f)

        for k, v in data.items():
            if k.startswith("urlopen:"):
                mock_response_class = MockedAddInfoURL
            else:
                mock_response_class = MockedHTTPResponse

            self[k] = mock_response_class.from_dict(v)

    def create_key(self, host, port, method, url, body):
        """Create key to get a request's response.

        :rtype str:
        """
        return "%s %s:%s%s %s" % (method, host, port, url, body)

    def create_key_for_urlopen(self, **kwargs):
        """Create a key for urlopen."""

        kwargs.setdefault("method", "")
        if not kwargs["data"]:
            kwargs["data"] = ""

        return "urlopen:{method}{url}{data}".format(**kwargs)

    def has_request(self, *args):
        """Return True if library has the request."""
        # TODO: remove this useless function
        return self.create_key(*args) in self

    def had_response(self):
        pass
