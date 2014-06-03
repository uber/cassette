import os

import mock

from cassette.cassette_library import (CassetteLibrary,
                                       DirectoryCassetteLibrary,
                                       FileCassetteLibrary)
from cassette.tests.base import (TEMPORARY_RESPONSES_FILENAME,
                                 TEMPORARY_RESPONSES_ROOT, TestCase)
from cassette.utils import JsonEncoder, YamlEncoder

BAD_DIRECTORY = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp.json')
BAD_FILE = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp')


class TestFileCassetteLibrary(TestCase):

    @mock.patch.object(FileCassetteLibrary, "load_file")
    def test_lazy_load(self, mock_load):
        """Verify that the file is lazily loaded."""

        FileCassetteLibrary(TEMPORARY_RESPONSES_FILENAME, 'yaml')
        self.assertEqual(mock_load.called, False)


class TestCassetteLibrary(TestCase):
    """Verify that CassetteLibrary creates the correct subclasses."""

    def setUp(self):
        self.clean_up()

    def tearDown(self):
        self.clean_up()

    def clean_up(self):
        """Clean up bad temporary files and directories."""
        if os.path.isdir(BAD_DIRECTORY):
            os.rmdir(BAD_DIRECTORY)
        elif os.path.isfile(BAD_FILE):
            os.remove(BAD_FILE)

    def create_bad_files(self):
        """Generate bad examples of a directory and file.

        This will generate a directory and file that will not be able to be used
        by CassetteLibrary.
        """
        if not os.path.exists(BAD_DIRECTORY):
            os.mkdir(BAD_DIRECTORY)

        if not os.path.exists(BAD_FILE):
            with open(BAD_FILE, 'w') as f:
                f.write('')

    def test_create_new_cassette_library_with_extension(self):
        """Verify correct encoder is attached to a file CassetteLibrary."""
        filename = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp.json')
        lib = CassetteLibrary.create_new_cassette_library(filename, '')
        self.assertTrue(isinstance(lib, FileCassetteLibrary))
        self.assertTrue(isinstance(lib.encoder, JsonEncoder))

        filename = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp.yaml')
        lib = CassetteLibrary.create_new_cassette_library(filename, '')
        self.assertTrue(isinstance(lib, FileCassetteLibrary))
        self.assertTrue(isinstance(lib.encoder, YamlEncoder))

    def test_create_new_cassette_library_with_directory(self):
        """Verify correct encoder is attached to a directory CassetteLibrary."""
        filename = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp')
        lib = CassetteLibrary.create_new_cassette_library(filename, '')
        self.assertTrue(isinstance(lib, DirectoryCassetteLibrary))
        self.assertTrue(isinstance(lib.encoder, JsonEncoder))

    def test_create_new_cassette_library_with_extension_and_file_type(self):
        """Verify correct encoder is attached with encoder override.

        Specifying file format takes precedent over the file extension.
        """
        # Manual enforcement of encoding overrides file type
        filename = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp.json')
        lib = CassetteLibrary.create_new_cassette_library(filename, 'yaml')
        self.assertTrue(isinstance(lib, FileCassetteLibrary))
        self.assertTrue(isinstance(lib.encoder, YamlEncoder))

        # Manual enforcement of encoding overrides file type
        filename = os.path.join(TEMPORARY_RESPONSES_ROOT, 'tmp.yaml')
        lib = CassetteLibrary.create_new_cassette_library(filename, 'json')
        self.assertTrue(isinstance(lib, FileCassetteLibrary))
        self.assertTrue(isinstance(lib.encoder, JsonEncoder))

    def test_create_new_cassette_library_errors(self):
        """Verify correct errors are raised."""
        self.create_bad_files()

        # Check to see that proper error handling is occuring for malformed file
        with self.assertRaises(IOError):
            CassetteLibrary.create_new_cassette_library(BAD_FILE, '')

        with self.assertRaises(IOError):
            CassetteLibrary.create_new_cassette_library(BAD_DIRECTORY, '')

        # Check to see if unsupported encoding raises error
        with self.assertRaises(KeyError):
            CassetteLibrary.create_new_cassette_library(BAD_DIRECTORY, 'derp')
