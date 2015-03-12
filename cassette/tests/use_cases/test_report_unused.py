import urllib2
from cStringIO import StringIO

from cassette.player import Player


def test_report_unused():
    config = {'log_cassette_used': True}
    player = Player('./cassette/tests/data/requests/', config=config)
    with player.play():
        urllib2.urlopen('http://httpbin.org/get')

    content = StringIO()
    player.report_unused_cassettes(content)
    content.seek(0)
    expected = ('httplib_GET_httpbin.org_80__unused.json\n'
                'httplib_GET_httpbin.org_80__unused2.json')
    assert content.read() == expected
