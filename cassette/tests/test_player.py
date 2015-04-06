import os
import shutil
import urllib2

import pytest

from cassette.exceptions import AttemptedConnectionException
from cassette.player import NO_HTTP_CONNECTION, Player
from cassette.tests.test_cassette import TEMPORARY_RESPONSES_DIRECTORY


@pytest.fixture(scope="module", autouse=True)
def cleanup_library(request):
    """Clean up the files."""
    def cleanup():
        filename = TEMPORARY_RESPONSES_DIRECTORY
        if os.path.exists(filename) and os.path.isdir(filename):
            shutil.rmtree(filename)

    cleanup()
    request.addfinalizer(cleanup)


def test_no_http_request():
    with Player(TEMPORARY_RESPONSES_DIRECTORY).play(mode=NO_HTTP_CONNECTION):
        with pytest.raises(AttemptedConnectionException):
            urllib2.urlopen('https://httpbin.org/ip')
