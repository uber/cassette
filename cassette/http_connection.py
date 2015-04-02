"""Contains mock HTTPConnection objects that imitate the behavior of
HTTPConnection from httplib. Cassette works by monkeypatching HTTPConnection
to check if a certain request has been cached already.

Note that although requests, urllib3 and urllib2 all use httplib, urllib3
uses its own, subclassed, version of HTTPConnection. So to make requests work,
we need to mock and patch this object.
"""
import logging
import socket
import ssl
from httplib import HTTPConnection, HTTPSConnection

import semver

log = logging.getLogger("cassette")


class CassetteConnectionMixin(object):
    _delete_sock_when_returning_from_library = False

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

            if self._delete_sock_when_returning_from_library:
                if hasattr(self, 'sock') and self.sock is None:
                    delattr(self, 'sock')

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


class CassetteHTTPSConnectionPre279(CassetteConnectionMixin, HTTPSConnection):

    _baseclass = HTTPSConnection

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        # Directly taken from httplib.
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file


class CassetteHTTPSConnectionPost279(CassetteConnectionMixin, HTTPSConnection):

    _baseclass = HTTPSConnection

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None, context=None):
        # Directly taken from httplib.
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file
        if context is None:
            context = ssl._create_default_https_context()
        if key_file or cert_file:
            context.load_cert_chain(cert_file, key_file)
        self._context = context

    def connect(self):
        "Connect to a host on a given (SSL) port."

        HTTPConnection.connect(self)

        if self._tunnel_host:
            server_hostname = self._tunnel_host
        else:
            server_hostname = self.host

        self.sock = self._context.wrap_socket(self.sock,
                                              server_hostname=server_hostname)


if hasattr(ssl, 'SSLContext'):
    CassetteHTTPSConnection = CassetteHTTPSConnectionPost279
else:
    CassetteHTTPSConnection = CassetteHTTPSConnectionPre279

try:
    from requests.packages import urllib3 as requests_urllib3
    import requests
except ImportError:
    pass
else:
    class UL3CassetteHTTPConnection(CassetteConnectionMixin,
                                    requests_urllib3.connection.HTTPConnection):

        _baseclass = requests_urllib3.connection.HTTPConnection
        # requests 2.3.0 and below have an issue where they get confused if
        # the HTTPConnection has a "sock" attribute which is set to None at
        # the end of a request/response cycle. So we delete the attribute in
        # those cases
        _delete_sock_when_returning_from_library = True if \
            semver.compare(requests.__version__, '2.4.0') == -1 else False

    class UL3CassetteHTTPSConnection(UL3CassetteHTTPConnection,
                                     CassetteConnectionMixin,
                                     requests_urllib3.connection.HTTPSConnection):

        _baseclass = requests_urllib3.connection.HTTPSConnection
