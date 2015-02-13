# -*- coding: utf8 -*-
"""
Test the cassette behavior.
"""

import httplib
import json
import os
import shutil
import threading
import urllib
import urllib2
import requests

import mock

import cassette
from cassette.cassette_library import CassetteLibrary
from cassette.tests.base import (TEMPORARY_RESPONSES_DIRECTORY,
                                 TEMPORARY_RESPONSES_FILENAME, TestCase)
from cassette.tests.server.run import app

IMAGE_FILENAME = "./cassette/tests/server/image.png"
TEST_HOST = "http://127.0.0.1:5000/"
TEST_URL = "http://127.0.0.1:5000/index"
TEST_URL_HTTPS = "https://httpbin.org/ip"
TEST_URL_REDIRECT = "http://127.0.0.1:5000/will_redirect"
TEST_URL_IMAGE = "http://127.0.0.1:5000/image"
TEST_URL_404 = "http://127.0.0.1:5000/404"
TEST_URL_HEADERS = "http://127.0.0.1:5000/headers"


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


class TestCassette(TestCase):
    """Testing the whole flow with a temporary response file."""

    # Keep track of a single HTTP server instance here so base classes don't
    # try to re-use the address.
    server_thread = None

    def setUp(self):
        self.filename = TEMPORARY_RESPONSES_FILENAME
        self.file_format = 'yaml'

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(self.filename):
            os.remove(self.filename)

    @classmethod
    def setUpClass(cls):
        if cls.server_thread is None:
            cls.server_thread = threading.Thread(
                target=app.run,
            )
            # Daemonizing will kill the thread when python exits.
            cls.server_thread.daemon = True
            cls.server_thread.start()

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def check_urllib2_flow(self, url, expected_content=None,
                           allow_incomplete_match=False,
                           data=None):
        """Verify the urllib2 flow."""

        if not url.startswith("http"):
            url = url_for(url)

        # First run
        with cassette.play(self.filename, file_format=self.file_format):
            r = urllib2.urlopen(url, data)  # 1st run

        self.assertEqual(self.had_response.called, False)
        if expected_content:
            content = unicode(r.read(), "utf-8")
            if allow_incomplete_match:
                self.assertIn(expected_content, content)
            else:
                self.assertEqual(content, expected_content)

        self.had_response.reset_mock()

        # Second run
        with cassette.play(self.filename, file_format=self.file_format):
            r = urllib2.urlopen(url, data)  # 2nd run

        self.assertEqual(self.had_response.called, True)
        if expected_content:
            content = unicode(r.read(), "utf-8")
            if allow_incomplete_match:
                self.assertIn(expected_content, content)
            else:
                self.assertEqual(content, expected_content)

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
        with cassette.play(self.filename, file_format=self.file_format):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()
            conn.close()

        self.assertEqual(r.status, 200)
        self.assertEqual(r.reason, "OK")
        self.assertEqual(r.read(), "hello world")
        self.assertEqual(self.had_response.called, False)

        self.had_response.reset_mock()

        # Second run
        with cassette.play(self.filename, file_format=self.file_format):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()
            conn.close()

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
        cassette.insert(self.filename, file_format=self.file_format)
        r = urllib2.urlopen(TEST_URL + '?manual')
        cassette.eject()

        self.assertEqual(self.had_response.called, False)
        self.assertEqual(r.read(), "hello world")

        self.had_response.reset_mock()

        # Second run
        cassette.insert(self.filename, file_format=self.file_format)
        r = urllib2.urlopen(TEST_URL + '?manual')
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

        url = "get?"
        url += _encode_params(param)
        r = self.check_urllib2_flow(url=url)
        self.assertEqual(r.json["args"]["param"], "1")

    def test_download_binary_file(self):
        """Verify that cassette can store a binary file (e.g. picture)"""

        # An image
        with open(IMAGE_FILENAME) as image_handle:
            expected_image = image_handle.read()

        # downloaded via urllib
        cassette.insert(self.filename, file_format=self.file_format)
        actual_image = urllib2.urlopen(TEST_URL_IMAGE).read()
        cassette.eject()

        # has a matching image
        self.assertEqual(self.had_response.called, False)
        self.assertEqual(expected_image, actual_image)

        self.had_response.reset_mock()

        # downloaded again via urllib
        cassette.insert(self.filename, file_format=self.file_format)
        actual_image = urllib2.urlopen(TEST_URL_IMAGE).read()
        cassette.eject()

        # still has a matching image
        self.assertEqual(self.had_response.called, True)
        self.assertEqual(expected_image, actual_image)

    def test_flow_404(self):
        """Verify that cassette can returns 404 from file."""

        # First run
        with cassette.play(self.filename, file_format=self.file_format):
            self.assertRaises(urllib2.HTTPError, urllib2.urlopen, TEST_URL_404)

        self.assertEqual(self.had_response.called, False)

        # Second run, it has the response.
        with cassette.play(self.filename, file_format=self.file_format):
            self.assertRaises(urllib2.HTTPError, urllib2.urlopen, TEST_URL_404)

        self.assertEqual(self.had_response.called, True)

    def helper_requestslib(self, url):
        with mock.patch.object(CassetteLibrary, '_had_response', autospec=True) as was_cached:
            with cassette.play(self.filename, file_format=self.file_format):
                r0 = requests.get(url)

            assert not was_cached.called

        with mock.patch.object(CassetteLibrary, '_had_response', autospec=True) as was_cached:
            with cassette.play(self.filename, file_format=self.file_format):
                r1 = requests.get(url)

                assert was_cached.called

        assert r0.text == r1.text
        return r1

    def test_requestslib_http(self):
        """Test that normal HTTP requests work using requests."""
        resp = self.helper_requestslib(TEST_URL)
        assert resp.headers['content-length'] == '11'
        assert resp.text == 'hello world'

    def test_requestslib_https(self):
        """Test that HTTPS requests work using requests."""
        resp = self.helper_requestslib(TEST_URL_HTTPS)
        # len('{\n  "origin":"0.0.0.0"\n}')  # 24
        assert int(resp.headers['content-length']) >= 24
        # len('{\n  "origin":  "255.255.255.255"\n}')  # 34
        assert int(resp.headers['content-length']) <= 34
        assert 'origin' in resp.json()

    def test_requestslib_redir(self):
        """Test that redirect behavior works using requests."""
        resp = self.helper_requestslib(TEST_URL_REDIRECT)
        assert resp.headers['content-length'] == '22'
        assert resp.text == 'hello world redirected'


class TestCassetteJson(TestCassette):
    """Perform the same test but in JSON."""

    def setUp(self):
        self.filename = TEMPORARY_RESPONSES_FILENAME
        self.file_format = 'json'

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(self.filename):
            os.remove(self.filename)


class TestCassetteDirectory(TestCassette):
    """Testing the whole flow with a temporary response directory in yaml."""

    def setUp(self):
        self.filename = TEMPORARY_RESPONSES_DIRECTORY
        self.file_format = 'yaml'

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            shutil.rmtree(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            shutil.rmtree(self.filename)


class TestCassetteDirectoryJson(TestCassetteDirectory):
    """Testing the whole flow with a temporary response directory in json."""

    def setUp(self):
        self.filename = TEMPORARY_RESPONSES_DIRECTORY
        self.file_format = 'json'

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            shutil.rmtree(self.filename)


class TestCassetteFile(TestCase):
    """Verify that cassette can read from an existing file. This is also
    the base test case for regression testing older versions of the schema.
    To avoid breaking test suites, new versions of cassette should always
    work with older schemas.
    """

    # The base class tests the most up to date schema.
    responses_filename = './cassette/tests/data/responses.yaml'

    def setUp(self):

        # This is a dummy method that we use to check if cassette had
        # the response.
        patcher = mock.patch.object(CassetteLibrary, "_had_response")
        self.had_response = patcher.start()
        self.addCleanup(patcher.stop)

    def check_read_from_file_flow(self, url, expected_content,
                                  allow_incomplete_match=False,
                                  request_headers=None):
        """Verify the flow when reading from an existing file."""

        with cassette.play(self.responses_filename):
            request = urllib2.Request(url, headers=request_headers or {})
            r = urllib2.urlopen(request)

        content = unicode(r.read(), "utf-8")
        if allow_incomplete_match:
            self.assertIn(expected_content, content)
        else:
            self.assertEqual(content, expected_content)
        self.assertEqual(self.had_response.called, True)

        return r

    def test_flow_urlopen(self):
        """Verify that cassette can read a file when using urlopen."""
        self.check_read_from_file_flow(TEST_URL, "hello world")

    def test_flow_httplib(self):
        """Verify that cassette can read a file when using httplib."""

        with cassette.play(self.responses_filename):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        self.assertEqual(r.status, 200)
        self.assertEqual(r.reason, "OK")
        self.assertEqual(r.read(), "hello world")
        self.assertEqual(self.had_response.called, True)

    def test_httplib_getheader_with_present_header(self):
        with cassette.play(self.responses_filename):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        assert r.getheader('content-length')

    def test_httplib_getheader_with_absent_header(self):
        with cassette.play(self.responses_filename):
            conn = httplib.HTTPConnection("127.0.0.1", 5000)
            conn.request("GET", "/index")
            r = conn.getresponse()

        assert r.getheader('X-FOOBAR') is None

    def test_read_twice(self):
        """Verify that response are not empty."""

        url = TEST_URL
        expected_content = "hello world"

        with cassette.play(self.responses_filename):
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

    def test_request_headers_json(self):
        """Verify that request headers are respected for application/json."""

        self.check_read_from_file_flow(
            url=TEST_URL_HEADERS,
            request_headers={"Accept": "application/json"},
            expected_content='"json": true',
            allow_incomplete_match=True)

    def test_request_headers_no_accept(self):
        """Verify that request headers are respected for default headers."""

        self.check_read_from_file_flow(
            url=TEST_URL_HEADERS,
            expected_content="not json")


class TestCassetteFile_0_3_2(TestCassetteFile):
    responses_filename = './cassette/tests/data/responses_0.3.2.yaml'
