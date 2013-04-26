import urllib2
import cassette
import os
from datetime import datetime, timedelta
from cassette.tests.base import TestCase

TEST_URL = "http://127.0.0.1:5000/non-ascii-content"
CASSETTE_FILENAME = './cassette/tests/data/performance.yaml'


class TestCassettePerformance(TestCase):
    @classmethod
    def teardown_class(cls):
        if os.path.exists(CASSETTE_FILENAME):
            os.remove(CASSETTE_FILENAME)

    def generate_large_cassette(self):
        # Record every next request
        cassette.insert(CASSETTE_FILENAME)

        # Create 100 requests to load in
        for i in range(0, 100):
            url = '%s?%s' % (TEST_URL, i)
            urllib2.urlopen(url).read()

        # Write out to files
        cassette.eject()

    def test_generate_speed(self):
        # Record how long it takes for the generation to take place
        start_time = datetime.now()
        self.generate_large_cassette()
        stop_time = datetime.now()

        # Verify the file generates in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)

    def fetch_frequent_cassette(self):
        # 100 times in a row
        for i in range(0, 100):
            # Open cassette
            cassette.insert(CASSETTE_FILENAME)

            # Make a few requests
            for j in range(0, 5):
                url = '%s?%s' % (TEST_URL, j)
                urllib2.urlopen(url).read()

            # Close cassette
            cassette.eject()

    def test_fetch_speed(self):
        # Guarantee there is a large cassette to test against
        if not os.path.exists(CASSETTE_FILENAME):
            self.generate_large_cassette()

        # Record how long it takes to fetch from a file frequently
        start_time = datetime.now()
        self.fetch_frequent_cassette()
        stop_time = datetime.now()

        # Verify the frequent fetches can run in under 2 seconds
        two_seconds = timedelta(seconds=2)
        self.assertLess(stop_time - start_time, two_seconds)
