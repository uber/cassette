import mock

from cassette.tests.base import TestCase
from cassette.tests.base import TEMPORARY_RESPONSES_FILENAME
from cassette.cassette_library import FileCassetteLibrary


class TestFileCassetteLibrary(TestCase):

    @mock.patch.object(FileCassetteLibrary, "load_file")
    def test_lazy_load(self, mock_load):
        """Verify that the file is lazily loaded."""

        FileCassetteLibrary(TEMPORARY_RESPONSES_FILENAME, 'yaml')
        self.assertEqual(mock_load.called, False)
