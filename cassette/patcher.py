from __future__ import absolute_import

import httplib

try:
    import requests
except ImportError:
    requests = None
else:
    from cassette.http_connection import (UL3CassetteHTTPConnection,
                                          UL3CassetteHTTPSConnection)

from cassette import http_connection


unpatched_HTTPConnection = httplib.HTTPConnection
unpatched_HTTPSConnection = httplib.HTTPSConnection
if requests:
    unpatched_requests_HTTPConnection = (requests.packages
                                         .urllib3.connection.HTTPConnection)
    unpatched_requests_HTTPSConnection = (requests.packages
                                          .urllib3.connection.HTTPSConnection)


def patch(cassette_library, ensure_no_http_requests=False):
    """Replace standard library."""
    # This part is inspired by vcrpy

    http_connection.CassetteHTTPConnection._cassette_library = cassette_library
    http_connection.CassetteHTTPSConnection._cassette_library = cassette_library  # noqa

    if ensure_no_http_requests:
        http_klass = http_connection.CassetteEnsureNoHTTPConnection
        https_klass = http_connection.CassetteEnsureNoHTTPConnection
    else:
        http_klass = http_connection.CassetteHTTPConnection
        https_klass = http_connection.CassetteHTTPSConnection

    httplib.HTTPConnection = http_klass
    httplib.HTTP._connection_class = http_klass
    httplib.HTTPSConnection = https_klass
    httplib.HTTPS._connection_class = https_klass

    if requests:
        UL3CassetteHTTPConnection._cassette_library = cassette_library
        UL3CassetteHTTPSConnection._cassette_library = cassette_library

        requests.packages.urllib3.connectionpool.HTTPConnectionPool.ConnectionCls = \
            UL3CassetteHTTPConnection
        requests.packages.urllib3.connectionpool.HTTPSConnectionPool.ConnectionCls = \
            UL3CassetteHTTPSConnection


def unpatch():
    """Unpatch standard library."""
    # This part is inspired by vcrpy

    httplib.HTTPConnection = unpatched_HTTPConnection
    httplib.HTTP._connection_class = unpatched_HTTPConnection
    httplib.HTTPSConnection = unpatched_HTTPSConnection
    httplib.HTTPS._connection_class = unpatched_HTTPSConnection

    if requests:
        requests.packages.urllib3.connection.HTTPConnection = unpatched_requests_HTTPConnection  # noqa
        requests.packages.urllib3.connection.HTTPSConnection = unpatched_requests_HTTPSConnection  # noqa
