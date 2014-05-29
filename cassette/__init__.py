from __future__ import absolute_import
import contextlib
import logging

from cassette.cassette_library import CassetteLibrary
from cassette.patcher import patch, unpatch

cassette_library = None
logging.getLogger("cassette").addHandler(logging.NullHandler())


def insert(filename, encoding='yaml'):
    """Setup cassette.

    :param filename: path to .yaml where requests and responses will be stored.
    """
    global cassette_library

    cassette_library = CassetteLibrary(filename, encoding=encoding)
    patch(cassette_library)


def eject():
    """Remove cassette, unpatching HTTP requests."""

    # If the cassette items have changed, save the changes to file
    if cassette_library.is_dirty:
        cassette_library.write_to_file()

    # Remove our overrides
    unpatch()


@contextlib.contextmanager
def play(filename, encoding='yaml'):
    """Use cassette."""
    insert(filename, encoding=encoding)
    yield
    eject()
