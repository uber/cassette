from io import StringIO
from httplib import HTTPMessage

from cassette.mocked_response import MockedResponse


class MockedHTTPResponse(MockedResponse):

    attrs = ("headers", "content", "status", "reason", "raw_headers")

    @classmethod
    def from_response(cls, response):
        """Create object from true response."""

        d = {
            "headers": dict(response.getheaders()),
            "content": response.read(),
            "status": response.status,
            "reason": response.reason,
            "raw_headers": response.msg.headers,
        }
        return cls.from_dict(d)

    @classmethod
    def from_dict(cls, data):
        """Create object from dict."""

        obj = cls()

        for k in cls.attrs:
            setattr(obj, k, data[k])

        # obj.content = obj.content.decode("utf-8")
        obj.fp = StringIO(unicode(obj.content, "utf-8"))

        obj.msg = HTTPMessage(StringIO(unicode()), 0)
        for k, v in obj.headers.iteritems():
            obj.msg.addheader(k, v)

        obj.msg.headers = data["raw_headers"]

        return obj

    def read(self, chunked=None):
        return self.fp.read()

    def getheaders(self):
        return self.headers.items()

    def getheader(self, name):
        return self.headers[name]

    def close(self):
        pass
