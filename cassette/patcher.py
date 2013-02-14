from __future__ import absolute_import
import urllib2
import httplib

from cassette.urlopen import CassetteURLOpen
from cassette.http_connection import CassetteHTTPConnection, CassetteHTTPSConnection

unpatched_urlopen = urllib2.urlopen
unpatched_HTTPConnection = httplib.HTTPConnection
unpatched_HTTPSConnection = httplib.HTTPSConnection


def patch(cassette_library):
    """Replace standard library."""

    urllib2.urlopen = CassetteURLOpen(cassette_library)

    # Taken from vcrpy

    CassetteHTTPConnection._cassette_library = cassette_library
    CassetteHTTPSConnection._cassette_library = cassette_library

    httplib.HTTPConnection = CassetteHTTPConnection
    httplib.HTTP._connection_class = CassetteHTTPConnection
    httplib.HTTPSConnection = CassetteHTTPSConnection
    httplib.HTTPS._connection_class = CassetteHTTPSConnection


def unpatch():
    """Unpatch standard library."""

    urllib2.urlopen = unpatched_urlopen

    # Taken from vcrpy

    httplib.HTTPConnection = unpatched_HTTPConnection
    httplib.HTTP._connection_class = unpatched_HTTPConnection
    httplib.HTTPSConnection = unpatched_HTTPSConnection
    httplib.HTTPS._connection_class = unpatched_HTTPSConnection
