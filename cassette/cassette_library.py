from __future__ import absolute_import
import logging
import os
import hashlib

import json
import yaml

from cassette.http_response import MockedHTTPResponse
from cassette.utils import json_str_decode_dict
from cassette.utils import TEXT_ENCODING

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
    def from_httplib_connection(cls, host, port, method, url, body,
                                headers, hash_body=False):
        """Create an object from an httplib request."""

        if headers:
            headers = hashlib.md5(repr(sorted(headers.items()))).hexdigest()

        # note that old yaml files will not contain the correct matching body
        if hash_body:
            if body:
                body = hashlib.md5(body).hexdigest()
            else:
                body = ''

        name = "httplib:{method} {host}:{port}{url} {headers} {body}".format(**locals())
        name = name.strip()
        return name


class CassetteLibrary(object):
    """
    The CassetteLibrary holds the stored requests and manage them.

    :param str filename: filename to use when storing and replaying requests.

    """

    cache = {}

    def __init__(self, filename, encoding='yaml'):
        self.filename = os.path.abspath(filename)
        self.is_dirty = False

        # Note: if file/directory doesn't exist, default to file
        self.is_directory = os.path.isdir(self.filename)

        self.encoding = encoding

    @property
    def data(self):
        """Lazily loaded data."""

        if not hasattr(self, "_data"):
            if self.is_directory:
                # each key is a file, hence will fetch when needed
                self._data = {}
            else:
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
        if self.is_directory:
            self.write_to_directory()
        else:
            self.write_to_single_file()

        self.is_dirty = False

    def write_to_directory(self):
        """Write mocked response to a directory of files."""

        # Here key=request, value=response
        for cassette_name, response in self.data.items():
            filename = self.generate_filename(cassette_name)
            # TODO: abstract encoding type
            # Serialize the items via YAML
            encoded_str = self.dump(response.to_dict())

            try:
                with open(os.path.join(self.filename, filename), 'w+') as f:
                    f.write(encoded_str)
            except:
                # this should never happen since the directory must be there
                # since it defaults to single file when the dir is not there
                raise IOError("Directory containing file '{f}' does not \
                        exist.".format(f=self.filename))

            self.save_to_cache(file_hash=_hash(encoded_str), data=response)

    def write_to_single_file(self):
        """Write mocked responses to file."""

        # Serialize the items via YAML
        data = {k: v.to_dict() for k, v in self.data.items()}
        encoded_str = self.dump(data)

        # Save the changes to file
        try:
            with open(self.filename, "w+") as f:
                f.write(encoded_str)
        except:
            raise IOError("Directory containing file '{f}' does not \
                    exist.".format(f=self.filename))

        # Update our hash
        self.save_to_cache(file_hash=_hash(encoded_str), data=self.data)

    def load_file(self):
        """Load MockedResponses from YAML file."""

        data = {}
        filename = self.filename

        if not os.path.exists(filename):
            log.info("File '{f}' does not exist.".format(f=filename))
            return data

        # Open and read in the file
        with open(filename) as f:
            encoded_str = f.read()
        encoded_hash = _hash(encoded_str)

        # If the contents are cached, return them
        cached_result = CassetteLibrary.cache.get(filename, None)
        if cached_result and cached_result['hash'] == encoded_hash:
            return cached_result['data']

        # Otherwise, parse the contents
        content = self.load_str(encoded_str)

        if content:
            for k, v in content.items():
                mock_response_class = MockedHTTPResponse
                data[k] = mock_response_class.from_dict(v)

        # Cache the file for later
        self.save_to_cache(file_hash=encoded_hash, data=data)

        return data

    def cassette_name_for_httplib_connection(self, host, port, method,
                                             url, body, headers):
        """Create a cassette name from an httplib request."""
        return CassetteName.from_httplib_connection(
            host, port, method, url, body, headers, hash_body=self.is_directory)

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
        if self.is_directory:
            return self._name_in_directory(cassette_name)
        return self._name_in_file(cassette_name)

    def _name_in_file(self, cassette_name):
        contains = cassette_name in self.data

        if contains:
            self._had_response()  # For testing purposes
            log.info("Library has '{n}'".format(n=cassette_name))
        else:
            log.warning("Library does not have '{n}'".format(n=cassette_name))

        return contains

    def _name_in_directory(self, cassette_name):
        contains = cassette_name in self.data

        if not contains:
            # Check file directory if it exists

            filename = os.path.join(
                self.filename, self.generate_filename(cassette_name))

            contains = os.path.exists(filename)

        if contains:
            self._had_response()  # For testing purposes
            log.info("Library has '{n}'".format(n=cassette_name))
        else:
            log.warning("Library does not have '{n}'".format(n=cassette_name))

        return contains

    def __getitem__(self, cassette_name):
        if self.is_directory:
            return self._getitem_from_directory(cassette_name)
        return self._getitem_from_file(cassette_name)

    def _getitem_from_file(self, cassette_name):
        """
        Fetch the request from the dictionary data that has already been loaded.
        """
        req = self.data.get(cassette_name, None)

        if req:
            req.rewind()

        return req

    def _getitem_from_directory(self, cassette_name):
        """
        Fetch the request from self.data if it exists. Otherwise, look to disk.
        """
        if cassette_name in self.data:
            req = self.data[cassette_name]
        else:
            # If not in self.data, need to fetch from disk
            req = self.load_request_from_file(cassette_name)

        if req:
            req.rewind()

        return req

    def load_request_from_file(self, cassette_name):
        """
        If the cassette file is in the cache, then use it. Otherwise, read
        from the disk to fetch the particular request.

        Returns the mocked response object from a YAML file.
        """

        filename = os.path.join(
            self.filename, self.generate_filename(cassette_name))

        if not os.path.exists(filename):
            log.info("File '{f}' does not exist.".format(f=filename))
            return None

        with open(filename) as f:
            encoded_str = f.read()
        encoded_hash = _hash(encoded_str)

        # If the contents are cached, return them
        cached_result = CassetteLibrary.cache.get(filename, None)
        if cached_result and cached_result['hash'] == encoded_hash:
            return cached_result['data']

        # Otherwise, parse the contents
        content = self.load_str(encoded_str)

        if content:
            mock_response_class = MockedHTTPResponse
            req = mock_response_class.from_dict(content)

        # Cache the file for later
        self.save_to_cache(file_hash=encoded_hash, data=req)
        return req

    def dump(self, data):
        if self.encoding == 'json':
            return json.dumps(data, ensure_ascii=False)
        return yaml.dump(data)

    def load_str(self, encoded_str):
        if self.encoding == 'json':
            return json.loads(encoded_str, TEXT_ENCODING,
                              object_hook=json_str_decode_dict)
        return yaml.load(encoded_str)

    def generate_filename(self, filename):
        for ch in ['/', ':', ' ']:
            filename = filename.replace(ch, '_')

        if self.encoding == 'json':
            return filename + '.json'
        return filename + '.yaml'
