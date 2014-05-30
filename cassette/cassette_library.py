from __future__ import absolute_import
import logging
import os
import hashlib

from cassette.http_response import MockedHTTPResponse
from cassette.utils import JsonEncoder
from cassette.utils import YamlEncoder

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
            headers = hashlib.md5(repr(sorted(headers.items()))).hexdigest()

        # note that old yaml files will not contain the correct matching body
        if will_hash_body:
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

    This is an abstract class that needs to have several methods implemented.

    :param str filename: filename to use when storing and replaying requests.
    :param str encoding: the encoding to use for storing the responses.
    """

    # TODO: what about enforcing self.data to be implemented somehow
    cache = {}

    def __init__(self, filename, encoding):
        self.filename = os.path.abspath(filename)
        self.is_dirty = False

        if encoding == 'json':
            self.encoder = JsonEncoder()
        else:
            self.encoder = YamlEncoder()

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

    # Methods that need to be implemented by subclasses
    def write_to_file(self):
        """Write the response data to file."""
        self.is_dirty = False
        raise NotImplementedError('CassetteLibrary not implemented.')

    def __contains__(self, cassette_name):
        raise NotImplementedError('CassetteLibrary not implemented.')

    def __getitem__(self, cassette_name):
        raise NotImplementedError('CassetteLibrary not implemented.')

    # Static methods
    @staticmethod
    def create_new_cassette_library(filename, encoding):
        """Returns an instantiated CassetteLibrary.

        Use this method to create new a CassetteLibrary. It will automatically
        determine if it should use a file or directory to back the cassette
        based on the filename. The method assumes that all file names with an
        extension (e.g. /file.json) are files, and all file names without
        extensions are directories (e.g. /testdir).


        :param str filename: filename of file or directory for storing requests
        :param str encoding: the encoding to use for storing requests
        """
        if encoding not in ('json', 'yaml', ''):
            raise KeyError("'{e}' is not a supported encoding.\
                    ".format(e=encoding))

        _, extension = os.path.splitext(filename)

        # Check if file has extension
        if extension:
            # If it has an extension, we assume filename is a file
            return CassetteLibrary._process_file(filename, encoding, extension)
        else:
            # Otherwise, we assume filename is a directory
            return CassetteLibrary._process_directory(filename, encoding)

    @staticmethod
    def _process_file(filename, encoding, extension):
        if os.path.isdir(filename):
            raise IOError("Expected a file, but found a directory at \
                    '{f}'".format(f=filename))

        # Parse encoding type
        if not encoding:
            if extension.lower() == JsonEncoder.file_ext:
                encoding = 'json'
            elif extension.lower() == YamlEncoder.file_ext:
                encoding = 'yaml'
            else:
                # Default to YAML for legacy code
                encoding = 'yaml'

        return FileCassetteLibrary(filename, encoding)

    @staticmethod
    def _process_directory(filename, encoding):
        if os.path.isfile(filename):
            raise IOError("Expected a directory, but found a file at \
                    '{f}'".format(f=filename))

        if encoding is None:
            encoding = 'json'  # default new directories to json

        return DirectoryCassetteLibrary(filename, encoding)


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
        try:
            with open(self.filename, "w+") as f:
                f.write(encoded_str)
        except:
            raise IOError("Directory containing file '{f}' does not \
                    exist.".format(f=self.filename))

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

        if contains:
            self._had_response()  # For testing purposes
            log.info("Library has '{n}'".format(n=cassette_name))
        else:
            log.warning("Library does not have '{n}'".format(n=cassette_name))

        return contains

    def __getitem__(self, cassette_name):
        """Fetch the request from the loaded dictionary data."""
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

    def write_to_file(self):
        """Write mocked response to a directory of files."""
        for cassette_name, response in self.data.items():
            filename = self.generate_filename(cassette_name)
            encoded_str = self.encoder.dump(response.to_dict())

            try:
                with open(os.path.join(self.filename, filename), 'w+') as f:
                    f.write(encoded_str)
            except:
                # this should never happen since the directory must be there
                # since it defaults to single file when the dir is not there
                raise IOError("Directory containing file '{f}' does not \
                        exist.".format(f=self.filename))

            # Update our hash
            self.save_to_cache(file_hash=_hash(encoded_str), data=response)

        self.is_dirty = False

    def __contains__(self, cassette_name):
        """Returns whether or not the cassette already exists.

        The method first checks if it is already stored in memory. If not, it
        will check if a file supporting the cassette name exists.
        """
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
        """Fetch the request if it exists in memory. Otherwise, look to disk."""
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
        """Returns the mocked response object from the encoded file.

        If the cassette file is in the cache, then use it. Otherwise, read
        from the disk to fetch the particular request."""

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
