from __future__ import absolute_import
import logging
import os
import hashlib

import yaml

from cassette.http_response import MockedHTTPResponse

log = logging.getLogger("cassette")


def _hash(content):
    m = hashlib.md5()
    m.update(content)
    return m.digest()


class CassetteName(unicode):

    """
    A CassetteName represents an unique way to retrieve the cassette
    from the library.
    """

    @classmethod
    def from_httplib_connection(cls, host, port, method, url, body, headers):
        """Create an object from an httplib request."""

        if headers:
            headers = hashlib.md5(repr(sorted(headers.items()))).hexdigest()

        name = "httplib:{method} {host}:{port}{url} {headers} {body}".format(**locals())
        name = name.strip()
        return name


class CassetteLibrary(object):
    """
    The CassetteLibrary holds the stored requests and manage them.

    :param str filename: filename to use when storing and replaying requests.

    """

    cache = {}

    def __init__(self, filename):
        self.filename = os.path.abspath(filename)
        self.is_dirty = False

    @property
    def data(self):
        """Lazily loaded data."""

        if not hasattr(self, "_data"):
            self._data = self.load_file()

        return self._data

    def add_response(self, cassette_name, response):
        """Add a new response to the mocked response.

        :param str cassette_name:
        :param response:
        """

        if not cassette_name:
            raise TypeError("No cassette name provided.")

        mock_response_class = MockedHTTPResponse
        mocked = mock_response_class.from_response(response)
        self.data[cassette_name] = mocked

        # Mark the cassette changes as dirty for ejection
        self.is_dirty = True

        return mocked

    def save_to_cache(self, file_hash, data):
        CassetteLibrary.cache[self.filename] = {
            'hash': file_hash,
            'data': data
        }

    def write_to_file(self):
        """Write mocked responses to file."""

        # Serialize the items via YAML
        data = {k: v.to_dict() for k, v in self.data.items()}
        yaml_str = yaml.dump(data)

        # Save the changes to file
        with open(self.filename, "w+") as f:
            f.write(yaml_str)

        # Update our hash
        self.save_to_cache(file_hash=_hash(yaml_str), data=self.data)

    def load_file(self):
        """Load MockedResponses from YAML file."""

        data = {}
        filename = self.filename

        if not os.path.exists(filename):
            log.info("File '%s' does not exist." % filename)
            return data

        # Open and read in the file
        with open(filename) as f:
            yaml_str = f.read()
        yaml_hash = _hash(yaml_str)

        # If the contents are cached, return them
        cached_result = CassetteLibrary.cache.get(filename, None)
        if cached_result and cached_result['hash'] == yaml_hash:
            return cached_result['data']

        # Otherwise, parse the contents
        content = yaml.load(yaml_str)

        if content:
            for k, v in content.items():
                mock_response_class = MockedHTTPResponse
                data[k] = mock_response_class.from_dict(v)

        # Cache the file for later
        self.save_to_cache(file_hash=yaml_hash, data=data)

        return data

    def cassette_name_for_httplib_connection(self, host, port, method,
                                             url, body, headers):
        """Create a cassette name from an httplib request."""
        return CassetteName.from_httplib_connection(
            host, port, method, url, body, headers)

    def rewind(self):
        for k, v in self.data.items():
            v.rewind()

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
        req = self.data[cassette_name]
        if req:
            req.rewind()
        return req
