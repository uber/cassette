import logging
import socket
from httplib import HTTPConnection, HTTPSConnection


class CassetteConnectionMixin(object):

    def request(self, method, url, body=None, headers={}):
        """Send HTTP request."""

        self._key = self._cassette_library.create_key(self.host,
                                                      self.port,
                                                      method, url, body)
        if self._cassette_library.has_request(self.host,
                                              self.port,
                                              method, url, body):
            self._response = self._cassette_library[self._key]

            # This is only for testing purposes
            self._cassette_library.had_response()
            return

        logging.debug("'%s' not in library, making HTTP request." % self._key)
        self._baseclass.request(self, method, url, body, headers)

    def getresponse(self, buffering=False):
        """Return HTTP response."""

        if buffering:
            raise NotImplemented("buffering not supported by cassette.")

        if hasattr(self, "_response"):
            return self._response

        response = HTTPConnection.getresponse(self)
        # If we were just returning the response here, the file
        # descriptor would be at the end of the file, and read() would
        # return nothing.
        response = self._cassette_library.add_response(self._key, response)

        return response


class CassetteHTTPConnection(CassetteConnectionMixin, HTTPConnection):

    _baseclass = HTTPConnection

    def __init__(self, *args, **kwargs):
        HTTPConnection.__init__(self, *args, **kwargs)


class CassetteHTTPSConnection(CassetteConnectionMixin, HTTPSConnection):

    _baseclass = HTTPSConnection

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        # Directly taken from httplib.
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file
