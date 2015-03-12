from __future__ import absolute_import
import contextlib
import logging

from cassette.player import Player

player = None
logging.getLogger("cassette").addHandler(logging.NullHandler())


def insert(filename, file_format=''):
    """Setup cassette.

    :param filename: path to where requests and responses will be stored.
    """
    global player

    player = Player(filename, file_format)
    player.__enter__()


def eject(exc_type=None, exc_value=None, tb=None):
    """Remove cassette, unpatching HTTP requests."""
    player.__exit__(exc_type, exc_value, tb)


@contextlib.contextmanager
def play(filename, file_format=''):
    """Use cassette."""
    insert(filename, file_format=file_format)
    yield
    eject()
