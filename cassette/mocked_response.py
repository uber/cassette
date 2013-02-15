

class MockedResponse(object):

    def to_dict(self):
        """Return dict representation."""

        if not hasattr(self, "attrs"):
            raise AttributeError("You need to have an 'attrs' class attr.")

        return {k: getattr(self, k) for k in self.attrs}

    @classmethod
    def from_response(self, response):
        raise NotImplementedError

    def rewind(self):
        """Make sure the file description is at the start."""
        pass
