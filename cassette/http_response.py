from io import StringIO
from httplib import HTTPMessage


class MockedHTTPResponse(object):

    attrs = ("headers", "content", "status", "reason", "msg")

    @classmethod
    def from_response(cls, response):
        """Create object from true response."""

        obj = cls()

        obj.headers = dict(response.getheaders())
        obj.content = response.read()
        obj.status = response.status
        obj.reason = response.reason
        obj.fp = StringIO(unicode(obj.content))

        obj.msg = HTTPMessage(StringIO(unicode()))
        for k, v in obj.headers.iteritems():
            obj.msg.addheader(k, v)

        return obj

    @classmethod
    def from_dict(cls, data):
        """Create object from dict."""

        obj = cls()

        for k in cls.attrs:
            setattr(obj, k, data[k])

        obj.fp = StringIO(unicode(obj.content))

        return obj

    def to_dict(self):
        """Return dict representation."""
        return {k: getattr(self, k) for k in self.attrs}

    def read(self, chunked=None):
        return self.fp.read()

    def getheaders(self):
        return self.headers.items()

    def getheader(self, name):
        return self.headers[name]
