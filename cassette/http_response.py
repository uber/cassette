import io
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

        obj.fp = cls.create_file_descriptor(obj.content)

        obj.msg = HTTPMessage(io.StringIO(unicode()), 0)
        for k, v in obj.headers.iteritems():
            obj.msg.addheader(k, v)

        obj.msg.headers = data["raw_headers"]

        return obj

    @staticmethod
    def create_file_descriptor(content):
        """Create a file descriptor for content."""

        fp = io.BytesIO(content)

        return fp

    def read(self, chunked=None):
        return self.fp.read()

    def getheaders(self):
        return self.headers.items()

    def getheader(self, name):
        return self.headers.get(name)

    def rewind(self):
        self.fp = self.create_file_descriptor(self.content)
        self.read = self.fp.read
        return self

    def close(self):
        pass
