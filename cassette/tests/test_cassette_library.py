import mock

from cassette.tests.base import TestCase
from cassette.tests.base import TEMPORARY_RESPONSES_FILENAME
from cassette.cassette_library import CassetteLibrary


class TestCassetteLibrary(TestCase):

    @mock.patch.object(CassetteLibrary, "load_file")
    def test_lazy_load(self, mock_load):
        """Verify that the file is lazily loaded."""

        CassetteLibrary(TEMPORARY_RESPONSES_FILENAME)
        self.assertEqual(mock_load.called, False)
