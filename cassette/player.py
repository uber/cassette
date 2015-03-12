import sys

from cassette.cassette_library import CassetteLibrary
from cassette.patcher import patch, unpatch


class Player(object):

    def __init__(self, path, file_format='', config=None):
        self.library = CassetteLibrary.create_new_cassette_library(
            path, file_format, config)

    def play(self):
        """Return contextenv."""
        return self

    def __enter__(self):
        patch(self.library)

    def __exit__(self, exc_type, exc_value, tb):
        # If the cassette items have changed, save the changes to file
        if self.library.is_dirty:
            self.library.write_to_file()
        # Remove our overrides
        unpatch()

    def report_unused_cassettes(self, output=sys.stdout):
        """Report unused cassettes to file."""
        self.library.report_unused_cassettes(output)
