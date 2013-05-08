import urllib
import io

from cassette.mocked_response import MockedResponse


class MockedAddInfoURL(urllib.addinfourl, MockedResponse):
    """Subclass of this crazy addinfourl object that is defined in urllib."""

    attrs = ("url", "headers", "code", "content")

    @classmethod
    def create_fake(cls, url, headers, code, content):
        """Create a fake Response.

        This class method is needed so that we don't have to change the default
        constructor signature.
        """

        fp = cls.create_file_descriptor(content)

        # In urllib, constructor defined as
        # __init__(self, fp, headers, url, code=None)
        obj = cls(fp, headers, url, code)
        obj.content = content
        obj.read = fp.read

        return obj

    @classmethod
    def from_response(cls, info_url):
        """Create from an info_url object (returned by urllib2.urlopen)."""
        return cls.from_dict({
            "url": info_url.url,
            "headers": info_url.headers,
            "code": info_url.code,
            "content": info_url.read()
        })

    @classmethod
    def from_dict(cls, data):
        """Create from dict representation.

        :param dict data:
        """
        return cls.create_fake(**data)

    @staticmethod
    def create_file_descriptor(content):
        """Create a file descriptor for content. It attempts to use ASCII, then UTF8, then binary."""
        try:
            fp = io.StringIO(unicode(content))
        except UnicodeDecodeError:
            try:
                fp = io.StringIO(unicode(content, 'utf8'))
            except UnicodeDecodeError:
                fp = io.BytesIO(content)

        return fp

    def rewind(self):
        self.fp = self.create_file_descriptor(self.content)
        self.read = self.fp.read
        return self
