# -*- coding: utf8 -*-
"""
Test the cassette behavior.
"""

import httplib
import os
import unittest
import urllib2

import mock

import cassette
from cassette.cassette_library import CassetteLibrary


TEMPORARY_RESPONSES_FILENAME = "./cassette/tests/data/responses.temp.yaml"
RESPONSES_FILENAME = "./cassette/tests/data/responses.yaml"
TEST_URL = "http://127.0.0.1:5000/index"
TEST_URL_HTTPS = "https://www.fortify.net/sslcheck.html"
TEST_URL_REDIRECT = "http://127.0.0.1:5000/will_redirect"


class TestCassette(unittest.TestCase):

    def setUp(self):

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def tearDown(self):

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    #
    # Testing the whole flow with a temporary response file.
    #

    def check_urllib2_flow(self, url, expected_content,
                           allow_incomplete_match=False):
        """Verify the urllib2 flow."""

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(url)  # 1st run

        self.assertEqual(self.had_response.called, False)
        if allow_incomplete_match:
            self.assertIn(expected_content, r.read())
        else:
            self.assertEqual(r.read(), expected_content)

        self.had_response.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(url)  # 2nd run

        self.assertEqual(self.had_response.called, True)
        if allow_incomplete_match:
            self.assertIn(expected_content, r.read())
        else:
            self.assertEqual(r.read(), expected_content)

        return r

    def test_flow(self):
        """Verify that cassette works when using urllib2.urlopen."""
        self.check_urllib2_flow(TEST_URL, "hello world")

    def test_flow_redirected(self):
        """Verify that cassette works when redirected."""
        self.check_urllib2_flow(TEST_URL_REDIRECT, "hello world redirected")

    def test_flow_httplib(self):
        """Verify that cassette works when using httplib directly."""

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        self.assertEqual(r.status, 200)
        self.assertEqual(r.reason, "OK")
        self.assertEqual(r.read(), "hello world")
        self.assertEqual(self.had_response.called, False)

        self.had_response.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        self.assertEqual(r.status, 200)
        self.assertEqual(r.reason, "OK")
        self.assertEqual(r.read(), "hello world")
        self.assertEqual(self.had_response.called, True)

    def test_flow_https(self):
        """Verify the cassette behavior for HTTPS."""
        self.check_urllib2_flow(TEST_URL_HTTPS, "SSL Encryption Report",
                                allow_incomplete_match=True)

    def test_flow_manual_context(self):
        """Verify the cassette behavior when setting up the context."""

        # First run
        cassette.insert(TEMPORARY_RESPONSES_FILENAME)
        r = urllib2.urlopen(TEST_URL)
        cassette.eject()

        self.assertEqual(self.had_response.called, False)
        self.assertEqual(r.read(), "hello world")

        self.had_response.reset_mock()

        # Second run
        cassette.insert(TEMPORARY_RESPONSES_FILENAME)
        r = urllib2.urlopen(TEST_URL)
        cassette.eject()

        self.assertEqual(self.had_response.called, True)
        self.assertEqual(r.read(), "hello world")

    def test_flow_get_non_ascii_page(self):
        """Verify that cassette can store a non-ascii page."""
        self.check_urllib2_flow(
            url="http://127.0.0.1:5000/non-ascii-content",
            expected_content=u"Le Mexicain l'avait achetée en viager "
            u"à un procureur à la retraite. Après trois mois, "
            u"l'accident bête. Une affaire.")

    #
    # Verifying that cassette can read from an existing file.
    #

    def check_read_from_file_flow(self, url, expected_content,
                                  allow_incomplete_match=False):
        """Verify the flow when reading from an existing file."""

        with cassette.play(RESPONSES_FILENAME):
            r = urllib2.urlopen(url)

        self.assertEqual(self.had_response.called, True)
        if allow_incomplete_match:
            self.assertIn(expected_content, r.read())
        else:
            self.assertEqual(r.read(), expected_content)

        return r

    def test_read_file(self):
        """Verify that cassette can read a file."""
        self.check_read_from_file_flow(TEST_URL, "hello world")

    def test_read_twice(self):
        """Verify that response are not empty."""

        url = TEST_URL
        expected_content = "hello world"

        with cassette.play(RESPONSES_FILENAME):
            r = urllib2.urlopen(url)
            self.assertEqual(r.read(), expected_content)
            r = urllib2.urlopen(url)
            self.assertEqual(r.read(), expected_content)

    def test_read_file_https(self):
        """Verify that cassette can read a file for an HTTPS request."""
        self.check_read_from_file_flow(TEST_URL_HTTPS, "SSL Encryption Report",
                                       allow_incomplete_match=True)

    def test_redirects(self):
        """Verify that cassette can handle a redirect."""
        self.check_read_from_file_flow(TEST_URL_REDIRECT, "hello world redirected")

    def test_non_ascii_content(self):
        """Verify that cassette can handle non-ascii content."""

        self.check_read_from_file_flow(
            url="http://127.0.0.1:5000/non-ascii-content",
            expected_content=u"Le Mexicain l'avait achetée en viager "
            u"à un procureur à la retraite. Après trois mois, "
            u"l'accident bête. Une affaire.")
