# -*- coding: utf8 -*-
"""
Test the cassette behavior.
"""

import httplib
import json
import os
import unittest
import urllib
import urllib2

import mock

import cassette
from cassette.cassette_library import CassetteLibrary


TEMPORARY_RESPONSES_FILENAME = "./cassette/tests/data/responses.temp.yaml"
RESPONSES_FILENAME = "./cassette/tests/data/responses.yaml"
TEST_HOST = "http://127.0.0.1:5000/"
TEST_URL = "http://127.0.0.1:5000/index"
TEST_URL_HTTPS = "https://httpbin.org/ip"
TEST_URL_REDIRECT = "http://127.0.0.1:5000/will_redirect"


# Taken from requests
def to_key_val_list(value):
    """Take an object and test to see if it can be represented as a
    dictionary. If it can be, return a list of tuples, e.g.,

    ::

    >>> to_key_val_list([('key', 'val')])
    [('key', 'val')]
    >>> to_key_val_list({'key': 'val'})
    [('key', 'val')]
    >>> to_key_val_list('string')
    Traceback (most recent call last):
        ...
    ValueError: cannot encode objects that are not 2-tuples
    """

    if value is None:
        return None

    if isinstance(value, (str, bytes, bool, int)):
        raise ValueError('cannot encode objects that are not 2-tuples')

    if isinstance(value, dict):
        value = value.items()

    return list(value)


def _encode_params(data):
    """Encode parameters in a piece of data.

    Will successfully encode parameters when passed as a dict or a list of
    2-tuples. Order is retained if data is a list of 2-tuples but abritrary
    if parameters are supplied as a dict.
    """

    if isinstance(data, (str, bytes)):
        return data
    elif hasattr(data, 'read'):
        return data
    elif hasattr(data, '__iter__'):
        result = []
        for k, vs in to_key_val_list(data):
            if isinstance(vs, basestring) or not hasattr(vs, '__iter__'):
                vs = [vs]
            for v in vs:
                if v is not None:
                    result.append(
                        (k.encode('utf-8') if isinstance(k, str) else k,
                         v.encode('utf-8') if isinstance(v, str) else v))
        return urllib.urlencode(result, doseq=True)


def url_for(endpoint):
    """Return full URL for endpoint."""
    return TEST_HOST + endpoint

#
# Testing the whole flow with a temporary response file.
#


class TestCassette(unittest.TestCase):

    def setUp(self):

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def tearDown(self):

        if os.path.exists(TEMPORARY_RESPONSES_FILENAME):
            os.remove(TEMPORARY_RESPONSES_FILENAME)

    def check_urllib2_flow(self, url, expected_content=None,
                           allow_incomplete_match=False,
                           data=None):
        """Verify the urllib2 flow."""

        if not url.startswith("http"):
            url = url_for(url)

        # First run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(url, data)  # 1st run

        self.assertEqual(self.had_response.called, False)
        if expected_content:
            if allow_incomplete_match:
                self.assertIn(expected_content, r.read())
            else:
                self.assertEqual(r.read(), expected_content)

        self.had_response.reset_mock()

        # Second run
        with cassette.play(TEMPORARY_RESPONSES_FILENAME):
            r = urllib2.urlopen(url, data)  # 2nd run

        self.assertEqual(self.had_response.called, True)
        if expected_content:
            if allow_incomplete_match:
                self.assertIn(expected_content, r.read())
            else:
                self.assertEqual(r.read(), expected_content)

        if r.headers["Content-Type"] == "application/json":
            try:
                r.json = json.loads(r.read())
            except ValueError:
                pass

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
        self.check_urllib2_flow(TEST_URL_HTTPS, "origin",
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

    def test_flow_get_with_array_args(self):
        """Verify that cassette can store array args."""

        param = {
            "dict1": {"dict2": "dict3", "dict4": "dict5"},
            "array": ["item1", "item2"],
            "int": 1,
            "param": "1",
        }

        url = "/get?"
        url += _encode_params(param)
        r = self.check_urllib2_flow(url=url)
        self.assertEqual(r.json["args"]["param"], "1")

#
# Verify that cassette can read from an existing file.
#


class TestCassetteFile(unittest.TestCase):

    def setUp(self):

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

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

    def test_flow_urlopen(self):
        """Verify that cassette can read a file when using urlopen."""
        self.check_read_from_file_flow(TEST_URL, "hello world")

    def test_flow_httplib(self):
        """Verify that cassette can read a file when using httplib."""

        with cassette.play(RESPONSES_FILENAME):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        self.assertEqual(r.status, 200)
        self.assertEqual(r.reason, "OK")
        self.assertEqual(r.read(), "hello world")
        self.assertEqual(self.had_response.called, True)

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
        self.check_read_from_file_flow(TEST_URL_HTTPS, "origin",
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
