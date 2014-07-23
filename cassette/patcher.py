from __future__ import absolute_import

import httplib

from cassette.http_connection import (CassetteHTTPConnection,
                                      CassetteHTTPSConnection)

unpatched_HTTPConnection = httplib.HTTPConnection
unpatched_HTTPSConnection = httplib.HTTPSConnection


class AttemptedConnection(Exception):
    pass


def _raise_attempted_connection(*args, **kwargs):
    # If you are seeing this exception, one of your colleagues has kindly
    # requested that you do not attempt to utilize HTTP requests during the
    # running of this area of your tests.  Consider refactoring the code you
    # want to test so that the logic can be tested independently from the I/O,
    # in a unit level test.

    raise AttemptedConnection()


def patch(cassette_library, backfire=False):
    """Replace standard library."""

    # Inspired by vcrpy

    connection = CassetteHTTPConnection

    if backfire:
        connection = _raise_attempted_connection

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
