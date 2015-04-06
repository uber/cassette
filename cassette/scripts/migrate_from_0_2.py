import argparse
import ast
import logging
import os
from urlparse import urlparse

from cassette.cassette_library import CassetteName
from cassette.cassette_library import DirectoryCassetteLibrary
from cassette.cassette_library import FileCassetteLibrary
from cassette.utils import Encoder

logger = logging.getLogger('cassette')
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


def translate(key):
    """Translate key in new post 0.2 format."""
    # Example: httplib:GET httpbin.org:80/status/200 None
    key_items = key.split()

    method = key_items[0].split(':')[1]

    full_url = key_items[1]
    parsed = urlparse('http://' + full_url)
    host = parsed.hostname
    port = parsed.port

    full_path = '/' + '/'.join(full_url.split('/')[1:])

    body = key_items[-1]
    try:
        # To handle None
        body = ast.literal_eval(body)
    except (ValueError, SyntaxError):
        pass

    return CassetteName.from_httplib_connection(
        host=host,
        port=port,
        method=method,
        url=full_path,
        body=body,
        headers='',
        will_hash_body=True,
        include_headers=False,
    )


def load(path):
    _, extension = os.path.splitext(path)
    encoder = Encoder.get_encoder_from_extension(extension)
    library = FileCassetteLibrary(path, encoder)
    for key, value in library.data.iteritems():
        yield translate(key), value


def main(old_path, new_path):
    # We prefer to use yaml because we might be encoding binary.
    encoder = Encoder.get_encoder_from_file_format('yaml')
    library = DirectoryCassetteLibrary(new_path, encoder)
    for key, value in load(old_path):
        logger.info('Creating record for %s', key)
        library.add_response(key, value)

    library.write_to_file()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Migrate a file from version 0.2')
    parser.add_argument('path', help='0.2 file')
    parser.add_argument('new', help='new path')
    args = parser.parse_args()

    main(args.path, args.new)
