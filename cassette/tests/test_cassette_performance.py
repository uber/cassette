import os
import shutil
import urllib2
from datetime import datetime, timedelta
from unittest import skip

import cassette
from cassette.tests.base import TestCase

TEST_URL = "http://127.0.0.1:5000/non-ascii-content"
CASSETTE_FILE = './cassette/tests/data/performance.tmp'
CASSETTE_DIRECTORY = './cassette/tests/data/performancedir/'


@skip('Skipping performance tests')
class TestCassettePerformanceSingleFile(TestCase):
    """Benchmark performance of a single file cassette."""

    def setUp(self):
        self.filename = CASSETTE_FILE

        if os.path.exists(self.filename):
            os.remove(self.filename)

    def tearDown(self):
        # Tear down for every test case
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def generate_large_cassette_yaml(self):
        """Generate a large set of responses and store in YAML."""
        # Record every next request
        cassette.insert(self.filename)

        # Create 100 requests to load in
        for i in range(0, 100):
            url = '%s?%s' % (TEST_URL, i)
            urllib2.urlopen(url).read()

        # Write out to files
        cassette.eject()

    def generate_large_cassette_json(self):
        """Generate a large set of responses and store in JSON."""
        # Record every next request
        cassette.insert(self.filename, file_format='json')

        # Create 100 requests to load in
        for i in range(0, 100):
            url = '%s?%s' % (TEST_URL, i)
            urllib2.urlopen(url).read()

        # Write out to files
        cassette.eject()

    def test_generate_speed_yaml(self):
        """Verify YAML generation of large response set takes under 2 secs."""
        # Record how long it takes for the generation to take place
        start_time = datetime.now()
        self.generate_large_cassette_yaml()
        stop_time = datetime.now()

        # Verify the file generates in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)

    def fetch_frequent_cassette(self):
        """Make repeated fetches of the same url with YAML file storage."""
        # 100 times in a row
        for i in range(0, 100):
            # Open cassette
            cassette.insert(self.filename, file_format='yaml')

            # Make a few requests
            for j in range(0, 5):
                url = '%s?%s' % (TEST_URL, j)
                urllib2.urlopen(url).read()

            # Close cassette
            cassette.eject()

    def fetch_frequent_cassette_json(self):
        """Make repeated fetches of the same url in JSON file storage."""
        # 100 times in a row
        for i in range(0, 100):
            # Open cassette
            cassette.insert(self.filename, file_format='json')

            # Make a few requests
            for j in range(0, 5):
                url = '%s?%s' % (TEST_URL, j)
                urllib2.urlopen(url).read()

            # Close cassette
            cassette.eject()

    def test_fetch_speed_yaml(self):
        """Verify fetching repeated files in YAML takes under 2 secs."""
        # Guarantee there is a large cassette to test against
        if not os.path.exists(self.filename):
            self.generate_large_cassette_yaml()

        # Record how long it takes to fetch from a file frequently
        start_time = datetime.now()
        self.fetch_frequent_cassette()
        stop_time = datetime.now()

        # Verify the frequent fetches can run in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)

    def test_generate_speed_json(self):
        """Verify JSON generation of large response set takes under 2 secs."""
        # Record how long it takes for the generation to take place
        start_time = datetime.now()
        self.generate_large_cassette_json()
        stop_time = datetime.now()

        # Verify the file generates in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)

    def test_fetch_speed_json(self):
        """Verify fetching repeated files in JSON takes under 2 secs."""
        # Guarantee there is a large cassette to test against
        if not os.path.exists(self.filename):
            self.generate_large_cassette_json()

        # Record how long it takes to fetch from a file frequently
        start_time = datetime.now()
        self.fetch_frequent_cassette_json()
        stop_time = datetime.now()

        # Verify the frequent fetches can run in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)


class TestCassettePerformanceDirectory(TestCassettePerformanceSingleFile):
    """Perform the same tests but with a cassette backed by a directory."""

    def setUp(self):
        self.filename = CASSETTE_DIRECTORY

        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            shutil.rmtree(self.filename)

        os.mkdir(self.filename)

    def tearDown(self):
        # Tear down for every test case
        if os.path.exists(self.filename) and os.path.isdir(self.filename):
            shutil.rmtree(self.filename)
