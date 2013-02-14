from cassette import unpatched


class CassetteURLOpen(object):

    def __init__(self, cassette_library):
        self._cassette_library = cassette_library

    def __call__(self, url, data=None, timeout=None):
        """Fake urlopen function."""

        if isinstance(url, basestring):
            # The goal here is not assume anything else (e.g. we could
            # be pretty certain that if there's no data, the method is
            # "GET").
            key = self._cassette_library.create_key_for_urlopen(
                url=url, data=data)

        else:
            # url is a Request object
            key = self._cassette_library.create_key_for_urlopen(
                method=url.get_method(),
                url=url.get_full_url(),
                data=url.get_data())

        if key in self._cassette_library:
            self._cassette_library.had_response()
            return self._cassette_library[key]

        else:
            # We need to unpatch, otherwise we would be using our mocked
            # httplib.
            with unpatched.unpatched_httplib_context(self._cassette_library):
                r = self._cassette_library.add_response(
                    key,
                    unpatched.get_unpatched_urlopen()(url, data, timeout))

            return r
