import os
import httplib
import unittest
import urllib2

import mock

import cassette
from cassette.cassette import CassetteLibrary
from cassette.patcher import unpatched_HTTPConnection
from cassette.http_connection import CassetteHTTPConnection


TEMPORARY_RESPONSES_FILENAME = "./cassette/tests/data/responses.temp.yaml"
RESPONSES_FILENAME = "./cassette/tests/data/responses.yaml"
TEST_URL = "http://www.internic.net/domain/named.root"
TEST_URL_HTTPS = "https://www.internic.net/domain/named.root"


class TestMockedResponse(unittest.TestCase):

    def setUp(self):
        # # Ironically, this test requires access to Internet
        # conn = httplib.HTTPConnection("www.internic.net")
        # conn.request("GET", "/domain/named.root")
        # self.response = conn.getresponse()

        # # We're patching the real urlopen, not the one that is patched
        # # by cassette
        # patcher = mock.patch.object(
        #     CassetteHTTPConnection,
        #     "make_true_request",
        #     return_value=self.response)
        # self.had_response = patcher.start()
        # self.addCleanup(patcher.stop)

        patcher = mock.patch.object(CassetteLibrary, "had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def tearDown(self):

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def test_flow(self):
        """Verify the cassette behavior."""

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL)

        self.assertFalse(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

        self.had_response.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL)

        self.assertTrue(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

    def test_flow_https(self):
        """Verify the cassette behavior for HTTPS."""

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL_HTTPS)

        self.assertFalse(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

        self.had_response.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL_HTTPS)

        self.assertTrue(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

    def test_flow_manual_context(self):
        """Verify the cassette behavior when setting up the context."""

        # First run
        cassette.insert(TEMPORARY_RESPONSES_FILENAME)
        r = urllib2.urlopen(TEST_URL)
        cassette.eject()

        self.assertFalse(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

        self.had_response.reset_mock()

        # Second run
        cassette.insert(TEMPORARY_RESPONSES_FILENAME)
        r = urllib2.urlopen(TEST_URL)
        cassette.eject()

        self.assertTrue(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

    def test_read_file(self):
        """Verify that cassette can read a file."""

        with cassette.play(RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL)

        self.assertTrue(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

    def test_read_file_https(self):
        """Verify that cassette can read a file for an HTTPS request."""

        with cassette.play(RESPONSES_FILENAME):
            r = urllib2.urlopen(TEST_URL_HTTPS)

        self.assertTrue(self.had_response.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))
