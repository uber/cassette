"""Contains mock HTTPConnection objects that imitate the behavior of
HTTPConnection from httplib. Cassette works by monkeypatching HTTPConnection
to check if a certain request has been cached already.

Note that although requests, urllib3 and urllib2 all use httplib, urllib3
uses its own, subclassed, version of HTTPConnection. So to make requests work,
we need to mock and patch this object.
"""
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

            # urllib3 does some additional weirdness to the `sock` attribute
            # when the request method is called. Since we skip that method here,
            # this is a hack to make it ignore this and not break.
            #
            # TODO: If we're going to add more adaptors to this module, this
            # class shouldn't know anything about its parent classes.
            try:
                if (isinstance(self, UL3CassetteHTTPConnection) and
                        hasattr(self, 'sock')):
                    del self.sock
            except NameError:
                pass

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
        response = self._baseclass.getresponse(self)

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

try:
    from requests.packages import urllib3 as requests_urllib3
except ImportError:
    pass
else:
    class UL3CassetteHTTPConnection(CassetteConnectionMixin,
                                    requests_urllib3.connection.HTTPConnection):

        _baseclass = requests_urllib3.connection.HTTPConnection

    class UL3CassetteHTTPSConnection(UL3CassetteHTTPConnection,
                                     CassetteConnectionMixin,
                                     requests_urllib3.connection.HTTPSConnection):

        _baseclass = requests_urllib3.connection.HTTPSConnection
