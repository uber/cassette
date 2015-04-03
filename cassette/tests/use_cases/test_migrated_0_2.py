import urllib2

from cassette.player import Player


def test_read_migrated():
    """Verify we can read a directory generated from a 0.2 file."""
    config = {
        'only_recorded': True,
        'hash_include_headers': False,
    }
    player = Player('./cassette/tests/data/responses_0.2/', config=config)
    with player.play():
        urllib2.urlopen('http://httpbin.org/status/200')
        urllib2.urlopen('http://httpbin.org/status/201')
        urllib2.urlopen('http://httpbin.org/get?toaster=1')
        urllib2.urlopen('http://httpbin.org/post', 'toaster')
