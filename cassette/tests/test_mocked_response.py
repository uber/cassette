import os
import unittest
import urllib2

import mock

import cassette


TEMPORARY_RESPONSES_FILENAME = "./cassette/tests/data/responses.temp.yaml"
RESPONSES_FILENAME = "./cassette/tests/data/responses.yaml"


class MockedResponseTest(unittest.TestCase):

    def setUp(self):
        # Ironically, this test requires access to Internet
        self.response = urllib2.urlopen("http://www.internic.net/domain/named.root")

        # We're patching the real urlopen, not the one that is patched
        # by cassette
        patcher = mock.patch("cassette.cassette.old_urlopen", return_value=self.response)
        self.mocked_urlopen = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def test_flow(self):
        """Verify the cassette behavior."""

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen("http://www.internic.net/domain/named.root")

        self.assertTrue(self.mocked_urlopen.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

        self.mocked_urlopen.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen("http://www.internic.net/domain/named.root")

        self.assertFalse(self.mocked_urlopen.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))

    def test_read_file(self):
        """Verify that cassette can read a file."""

        with cassette.play(RESPONSES_FILENAME):
            r = urllib2.urlopen("http://www.internic.net/domain/named.root")

        self.assertFalse(self.mocked_urlopen.called)
        self.assertIn("A.ROOT-SERVERS.NET", r.read(100000))
