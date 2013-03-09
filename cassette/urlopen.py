import logging

from cassette import unpatched

log = logging.getLogger("cassette")


class CassetteURLOpen(object):

    def __init__(self, cassette_library):
        self._cassette_library = cassette_library

    def __call__(self, url, data=None, timeout=None):
        """Fake urlopen function."""

        lib = self._cassette_library
        cassette_name = lib.cassette_name_for_urlopen(url, data)

        if cassette_name in lib:
            response = lib[cassette_name]
            response = response.rewind()

        else:
            log.warning("Making external HTTP request: %s" % cassette_name)
            # We need to unpatch, otherwise we would be using our mocked
            # httplib.
            with unpatched.unpatched_httplib_context(lib):
                response = lib.add_response(
                    cassette_name,
                    unpatched.get_unpatched_urlopen()(url, data, timeout))

        return response
