from __future__ import absolute_import

import hashlib
import logging
import os
from urlparse import urlparse

from cassette.http_response import MockedHTTPResponse
from cassette.utils import Encoder, DEFAULT_ENCODER

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
                                headers, will_hash_body=False):
        """Create an object from an httplib request."""

        if headers:
            if 'Host' in headers:
                # 'Host' is already covered explicitly below, remove from the
                # hash so hostname/post are easy to change and sed the file
                del headers['Host']

            headers = hashlib.md5(repr(sorted(headers.items()))).hexdigest()

        if will_hash_body:
            if body:
                body = hashlib.md5(body).hexdigest()
            else:
                body = ''

            if url:
                # instantiated to 0.0.0.0 so we can parse
                parsed_url = urlparse('http://0.0.0.0' + url)
                url = parsed_url.path
                query = hashlib.md5(parsed_url.query + '#' + parsed_url.fragment).hexdigest()
            else:
                url = ''
                query = ''
            name = "httplib:{method} {host}:{port}{url} {query} {headers} {body}".format(**locals())
        else:
            # note that old yaml files will not contain the correct matching
            # query and body
            name = "httplib:{method} {host}:{port}{url} {headers} {body}".format(**locals())

        name = name.strip()
        return name


class CassetteLibrary(object):
    """
    The CassetteLibrary holds the stored requests and manage them.

    This is an abstract class that needs to have several methods implemented.
    In addition, subclasses must store request/response pairs as a keys and
    values as a dictionary in the property `self.data`

    :param str filename: filename to use when storing and replaying requests.
    :param Encoder encoder: the instantiated encodeder to use
    """

    cache = {}

    def __init__(self, filename, encoder):
        self.filename = os.path.abspath(filename)
        self.is_dirty = False

        self.encoder = encoder

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
        """Save a decoded data object into cache."""
        CassetteLibrary.cache[self.filename] = {
            'hash': file_hash,
            'data': data
        }

    def rewind(self):
        """Restore all responses to a re-seekable state."""
        for k, v in self.data.items():
            v.rewind()

    def _had_response(self):
        """Mark that the library already the response.

        This is for testing purposes (it's complicated to patch the unpatched
        version of urllib2/httplib).
        """
        pass

    def cassette_name_for_httplib_connection(self, host, port, method,
                                             url, body, headers):
        """Create a cassette name from an httplib request."""
        return CassetteName.from_httplib_connection(
            host, port, method, url, body, headers)

    def _log_contains(self, cassette_name, contains):
        """Logging for checking access to cassettes."""
        if contains:
            self._had_response()  # For testing purposes
            log.info("Library has '{n}'".format(n=cassette_name))
        else:
            log.warning("Library does not have '{n}'".format(n=cassette_name))

    # Methods that need to be implemented by subclasses
    def write_to_file(self):
        """Write the response data to file."""
        raise NotImplementedError('CassetteLibrary not implemented.')

    def __contains__(self, cassette_name):
        raise NotImplementedError('CassetteLibrary not implemented.')

    def __getitem__(self, cassette_name):
        raise NotImplementedError('CassetteLibrary not implemented.')

    # Static methods
    @staticmethod
    def create_new_cassette_library(filename, file_format):
        """Return an instantiated CassetteLibrary.

        Use this method to create new a CassetteLibrary. It will automatically
        determine if it should use a file or directory to back the cassette
        based on the filename. The method assumes that all file names with an
        extension (e.g. /file.json) are files, and all file names without
        extensions are directories (e.g. /testdir).

        :param str filename: filename of file or directory for storing requests
        :param str file_format: the file_format to use for storing requests
        """
        if not Encoder.is_supported_format(file_format):
            raise KeyError("'{e}' is not a supported file_format.\
                    ".format(e=file_format))

        _, extension = os.path.splitext(filename)

        # Check if file has extension
        if extension:
            # If it has an extension, we assume filename is a file
            return CassetteLibrary._process_file(filename, file_format, extension)
        else:
            # Otherwise, we assume filename is a directory
            return CassetteLibrary._process_directory(filename, file_format)

    @staticmethod
    def _process_file(filename, file_format, extension):
        """Return an instantiated FileCassetteLibrary with the correct encoder.

        :param str file_format:
        :param str extension:
        """
        if os.path.isdir(filename):
            raise IOError("Expected a file, but found a directory at \
                    '{f}'".format(f=filename))

        # Parse encoding type
        if not file_format:
            encoder = Encoder.get_encoder_from_extension(extension)
        else:
            encoder = Encoder.get_encoder_from_file_format(file_format)

        return FileCassetteLibrary(filename, encoder)

    @staticmethod
    def _process_directory(filename, file_format):
        """Return an instantiated DirectoryCassetteLibrary with the correct
        encoder.

        :param str file_format:
        """
        if os.path.isfile(filename):
            raise IOError("Expected a directory, but found a file at \
                    '{f}'".format(f=filename))

        if not file_format:
            encoder = DEFAULT_ENCODER  # default new directories to json
        else:
            encoder = Encoder.get_encoder_from_file_format(file_format)

        return DirectoryCassetteLibrary(filename, encoder)


class FileCassetteLibrary(CassetteLibrary):
    """A CassetteLibrary that stores and manages requests with a single file."""

    @property
    def data(self):
        """Lazily loaded data."""

        if not hasattr(self, "_data"):
            self._data = self.load_file()

        return self._data

    def write_to_file(self):
        """Write mocked responses to file."""

        # Serialize the items via YAML
        data = {k: v.to_dict() for k, v in self.data.items()}
        encoded_str = self.encoder.dump(data)

        # Save the changes to file
        with open(self.filename, "w+") as f:
            f.write(encoded_str)

        # Update our hash
        self.save_to_cache(file_hash=_hash(encoded_str), data=self.data)

        self.is_dirty = False

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
        content = self.encoder.load(encoded_str)

        if content:
            for k, v in content.items():
                mock_response_class = MockedHTTPResponse
                data[k] = mock_response_class.from_dict(v)

        # Cache the file for later
        self.save_to_cache(file_hash=encoded_hash, data=data)

        return data

    def __contains__(self, cassette_name):
        contains = cassette_name in self.data
        self._log_contains(cassette_name, contains)

        return contains

    def __getitem__(self, cassette_name):
        """Return the request from the loaded dictionary data."""
        req = self.data.get(cassette_name, None)

        if not req:
            raise KeyError("Cassette '{c}' does not exist in \
                    library.".format(c=cassette_name))

        req.rewind()
        return req


class DirectoryCassetteLibrary(CassetteLibrary):
    """A CassetteLibrary that stores and manages requests with directory."""

    def __init__(self, *args, **kwargs):
        super(DirectoryCassetteLibrary, self).__init__(*args, **kwargs)

        self.data = {}

    def generate_filename(self, cassette_name):
        """Generate the filename for a given cassette name."""
        for character in ('/', ':', ' '):
            cassette_name = cassette_name.replace(character, '_')

        return cassette_name + self.encoder.file_ext

    def generate_path_from_cassette_name(self, cassette_name):
        """Generate the full path to cassette file."""
        return os.path.join(
            self.filename, self.generate_filename(cassette_name))

    def write_to_file(self):
        """Write mocked response to a directory of files."""
        if not os.path.exists(self.filename):
            os.mkdir(self.filename)

        for cassette_name, response in self.data.items():
            filename = self.generate_filename(cassette_name)
            encoded_str = self.encoder.dump(response.to_dict())

            with open(os.path.join(self.filename, filename), 'w') as f:
                f.write(encoded_str)

            # Update our hash
            self.save_to_cache(file_hash=_hash(encoded_str), data=response)

        self.is_dirty = False

    def __contains__(self, cassette_name):
        """Return whether or not the cassette already exists.

        The method first checks if it is already stored in memory. If not, it
        will check if a file supporting the cassette name exists.
        """
        contains = cassette_name in self.data

        if not contains:
            # Check file directory if it exists
            filename = self.generate_path_from_cassette_name(cassette_name)

            contains = os.path.exists(filename)

        self._log_contains(cassette_name, contains)

        return contains

    def __getitem__(self, cassette_name):
        """Return the request if it is in memory. Otherwise, look to disk."""
        if cassette_name in self.data:
            req = self.data[cassette_name]
        else:
            # If not in self.data, need to fetch from disk
            req = self._load_request_from_file(cassette_name)

        if not req:
            raise KeyError("Cassette '{c}' does not exist in \
                    library.".format(c=cassette_name))

        req.rewind()
        return req

    def _load_request_from_file(self, cassette_name):
        """Return the mocked response object from the encoded file.

        If the cassette file is in the cache, then use it. Otherwise, read
        from the disk to fetch the particular request.
        """

        filename = self.generate_path_from_cassette_name(cassette_name)

        try:
            with open(filename) as f:
                encoded_str = f.read()
        except:
            return None

        encoded_hash = _hash(encoded_str)

        # If the contents are cached, return them
        cached_result = CassetteLibrary.cache.get(filename, None)
        if cached_result and cached_result['hash'] == encoded_hash:
            return cached_result['data']

        # Otherwise, parse the contents
        content = self.encoder.load(encoded_str)

        if content:
            mock_response_class = MockedHTTPResponse
            req = mock_response_class.from_dict(content)

        # Cache the file for later
        self.save_to_cache(file_hash=encoded_hash, data=req)
        return req

    # Override
    def cassette_name_for_httplib_connection(self, host, port, method,
                                             url, body, headers):
        """Create a cassette name from an httplib request."""
        return CassetteName.from_httplib_connection(
            host, port, method, url, body, headers, will_hash_body=True)
