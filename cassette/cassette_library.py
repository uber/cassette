from __future__ import absolute_import
import logging
import os
import urllib2

import yaml

from cassette.http_response import MockedHTTPResponse
from cassette.addinfourl import MockedAddInfoURL

old_urlopen = urllib2.urlopen
log = logging.getLogger("cassette")


class CassetteName(unicode):

    """
    A CassetteName represents an unique way to retrieve the cassette
    from the library.
    """

    @classmethod
    def from_urlopen_url(cls, url, data):
        """Create an object from a urlopen url."""
        req = urllib2.Request(url, data)
        return cls.from_urlopen_request(req)

    @classmethod
    def from_urlopen_request(cls, request, data=None):
        """Create an object from a urlopen request."""

        # From Python source code, urllib2.py:382
        if data is not None:
            request.add_data(data)

        data = request.get_data()
        if not data:
            data = ""

        template_vars = dict(
            method=request.get_method(),
            url=request.get_full_url(),
            data=data
        )

        name = "urlopen:{method} {url} {data}".format(**template_vars)
        name = name.strip()
        return name

    @classmethod
    def from_httplib_connection(cls, host, port, method, url, body):
        """Create an object from an httplib request."""

        name = "httplib:{method} {host}:{port}{url} {body}".format(**locals())
        name = name.strip()
        return name


class CassetteLibrary(object):

    def __init__(self, filename):
        """Create a CassetteLibrary object.

        :param str filename: filename to file holding fake response
        """

        self.filename = os.path.abspath(filename)
        self.data = self.load_file()

    def add_response(self, cassette_name, response):
        """Add a new response to the mocked response.

        :param str cassette_name:
        :param response:
        """

        if not cassette_name:
            raise TypeError("No cassette name provided.")

        # Choose the class based on the response class
        if hasattr(response, "getheaders"):
            # It's an httplib.HTTPResponse
            mock_response_class = MockedHTTPResponse

        else:
            mock_response_class = MockedAddInfoURL

        mocked = mock_response_class.from_response(response)
        self.data[cassette_name] = mocked
        # TODO: would be probably more efficient to write the file only
        # on certain occasion.
        self.write_to_file()

        return mocked

    def write_to_file(self):
        """Write mocked responses to file."""

        data = {k: v.to_dict() for k, v in self.data.items()}
        with open(self.filename, "w+") as f:
            yaml.dump(data, f)

    def load_file(self):
        """Load MockedResponses from YAML file."""

        data = {}

        if not os.path.exists(self.filename):
            log.info("File '%s' does not exist." % self.filename)
            return data

        with open(self.filename) as f:
            content = yaml.load(f)

        for k, v in content.items():
            if k.startswith("urlopen:"):
                mock_response_class = MockedAddInfoURL
            else:
                mock_response_class = MockedHTTPResponse

            data[k] = mock_response_class.from_dict(v)

        return data

    def cassette_name_for_urlopen(self, url_or_request, data):
        """Create a cassette name from a urlopen request."""

        if isinstance(url_or_request, basestring):
            name = CassetteName.from_urlopen_url(url_or_request, data)
        else:
            # url is a urllib2.Request object
            name = CassetteName.from_urlopen_request(url_or_request, data)

        return name

    def cassette_name_for_httplib_connection(self, host, port, method,
                                             url, body):
        """Create a cassette name from an httplib request."""
        return CassetteName.from_httplib_connection(
            host, port, method, url, body)

    def _had_response(self):
        """Mark that the library already the response.

        This is for testing purposes (it's complicated to patch the unpatched
        version of urllib2/httplib).
        """
        pass

    def __contains__(self, cassette_name):
        contains = cassette_name in self.data

        if contains:
            self._had_response()  # For testing purposes
            log.info("Library has '%s'" % cassette_name)

        else:
            log.warning("Library does not have '%s'" % cassette_name)

        return contains

    def __getitem__(self, cassette_name):
        return self.data[cassette_name]
