from __future__ import absolute_import

import httplib

from cassette.http_connection import (CassetteHTTPConnection,
                                      CassetteHTTPSConnection)

unpatched_HTTPConnection = httplib.HTTPConnection
unpatched_HTTPSConnection = httplib.HTTPSConnection


class AttemptedConnection(Exception):
    pass


def patch(cassette_library, backfire=False):
    """Replace standard library."""

    # Inspired by vcrpy

    connection = CassetteHTTPConnection

    if backfire:
        def nonetwork(*args, **kwargs):
            print (
                "Attempt to create HTTPConnection({}, {})"
                .format(args, kwargs)
            )
            raise AttemptedConnection()

        connection = nonetwork

    CassetteHTTPConnection._cassette_library = cassette_library
    CassetteHTTPSConnection._cassette_library = cassette_library

    httplib.HTTPConnection = connection
    httplib.HTTP._connection_class = connection
    httplib.HTTPSConnection = connection
    httplib.HTTPS._connection_class = connection


def unpatch():
    """Unpatch standard library."""

    # Inspired by vcrpy

    httplib.HTTPConnection = unpatched_HTTPConnection
    httplib.HTTP._connection_class = unpatched_HTTPConnection
    httplib.HTTPSConnection = unpatched_HTTPSConnection
    httplib.HTTPS._connection_class = unpatched_HTTPSConnection
