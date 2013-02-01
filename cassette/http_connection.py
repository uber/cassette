import logging
from httplib import HTTPConnection


class CassetteHTTPConnection(HTTPConnection):

    def request(self, method, url, body=None, headers={}):
        """Send HTTP request."""

        # import ipdb; ipdb.set_trace()
        self._key = self._cassette_library.create_key(self.host,
                                                      self.port,
                                                      method, url, body)
        if self._cassette_library.has_request(self.host,
                                              self.port,
                                              method, url, body):
            self._response = self._cassette_library[self._key]

            # This is only for testing purposes
            self._cassette_library.had_response()
            return

        logging.debug("'%s' not in library, making HTTP request." % self._key)
        HTTPConnection.request(self, method, url, body, headers)

    def getresponse(self, buffering=False):
        """Return HTTP response."""

        if buffering:
            raise NotImplemented("buffering not supported by cassette.")

        if hasattr(self, "_response"):
            return self._response

        response = HTTPConnection.getresponse(self)
        # Reading back to zero
        response = self._cassette_library.add_response(self._key, response)

        return response


class CassetteHTTPSConnection(CassetteHTTPConnection):
    pass
