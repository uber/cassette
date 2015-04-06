import sys

from cassette.cassette_library import CassetteLibrary
from cassette.patcher import patch, unpatch

NO_HTTP_CONNECTION = 'no_http_connection'


class Player(object):

    def __init__(self, path, file_format='', config=None):
        self.library = CassetteLibrary.create_new_cassette_library(
            path, file_format, config)

    def play(self, mode=None):
        """Return contextenv."""
        return PlayContext(mode, player=self)

    def report_unused_cassettes(self, output=sys.stdout):
        """Report unused cassettes to file."""
        self.library.report_unused_cassettes(output)

    def insert(self):
        """Start player."""
        return self.play().__enter__()

    def eject(self, exc_type, exc_value, tb):
        """Stop player."""
        return self.play().__exit__(exc_type, exc_value, tb)


class PlayContext(object):

    def __init__(self, mode, player):
        self.mode = mode
        self.player = player

    def __enter__(self):
        if self.mode == NO_HTTP_CONNECTION:
            patch(self.player.library, ensure_no_http_requests=True)
        else:
            patch(self.player.library)

    def __exit__(self, exc_type, exc_value, tb):
        # Remove our overrides first.
        unpatch()
        # If the cassette items have changed, save the changes to file
        if self.player.library.is_dirty:
            self.player.library.write_to_file()
