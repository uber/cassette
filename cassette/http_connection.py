import logging
import socket
from httplib import HTTPConnection, HTTPSConnection

log = logging.getLogger("cassette")


class CassetteConnectionMixin(object):

    def request(self, method, url, body=None, headers=None):
        """Send HTTP request."""

        lib = self._cassette_library
        self._cassette_name = lib.cassette_name_for_httplib_connection(
            host=self.host,
            port=self.port,
            method=method,
            url=url,
            body=body,
            headers=headers,
        )
        if self._cassette_name in lib:
            self._response = lib[self._cassette_name]
            return

        log.warning("Making external HTTP request: %s" % self._cassette_name)
        self._baseclass.request(self, method, url, body, headers or {})

    def getresponse(self, buffering=False):
        """Return HTTP response."""

        if buffering:
            raise NotImplemented("buffering not supported by cassette.")

        if hasattr(self, "_response"):
            return self._response

        lib = self._cassette_library
        response = HTTPConnection.getresponse(self)

        # If we were just returning the response here, the file
        # descriptor would be at the end of the file, and read() would
        # return nothing.
        response = lib.add_response(self._cassette_name, response)

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
