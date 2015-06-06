"""
    utils.py

    Helper functions.
"""
import json

import yaml

TEXT_ENCODING = 'ISO-8859-1'


class Encoder(object):
    """Abstract class for an encoder consumed by cassette."""

    # Used for matching filenames that correspond to the encoder
    file_ext = '.file'

    @staticmethod
    def is_supported_format(file_format):
        """Return whether the file format is supported.

        :param str file_format:
        """
        return file_format in SUPPORTED_FORMATS.keys() or file_format == ''

    @staticmethod
    def get_encoder_from_file_format(file_format):
        """Return the correct encoder that corresponds to the file format.

        :param str file_format:
        """
        return SUPPORTED_FORMATS.get(
            file_format.lower(), DEFAULT_COMPATIBLE_ENCODER)

    @staticmethod
    def get_encoder_from_extension(extension):
        """Return the correct encoder that corresponds to the file extension.

        :param str extension:
        """
        if not extension:
            # It's a dir.
            return DEFAULT_ENCODER

        file_format = extension.replace('.', '')
        return Encoder.get_encoder_from_file_format(file_format)

    def dump(self, data):
        """Abstract method for dumping objects into an encoded form."""
        raise NotImplementedError('Encoder not implemented.')

    def load(self, encoded_str):
        """Abstract method for dumping an encoded string into objects."""
        raise NotImplementedError('Encoder not implemented.')


class JsonEncoder(Encoder):
    """JSON encoder for storing HTTP responses in plain text."""

    file_ext = '.json'

    def dump(self, data):
        """Return a YAML encoded string of the data."""
        return json.dumps(data, indent=4, ensure_ascii=False)

    def load(self, encoded_str):
        """Return an object from the encoded JSON string."""
        return json.loads(encoded_str, TEXT_ENCODING,
                          object_hook=JsonEncoder.json_str_decode_dict)

    @staticmethod
    def json_str_decode_list(data):
        """Decode the list portion of a JSON blob as a string."""

        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode(TEXT_ENCODING)
            elif isinstance(item, list):
                item = JsonEncoder.json_str_decode_list(item)
            elif isinstance(item, dict):
                item = JsonEncoder.json_str_decode_dict(item)
            rv.append(item)
        return rv

    @staticmethod
    def json_str_decode_dict(data):
        """Decode the dictionary portion of a JSON blob as a string.

        This helper function is necessary to decode the data as an ASCII string
        instead of a unicode string, which is required in order to be consumed
        by the mock HTTP response.
        """
        # Original code is from stackoverflow:
        # http://stackoverflow.com/questions/956867/how-to-get-string-objects-i
        # nstead-of-unicode-ones-from-json-in-python

        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode(TEXT_ENCODING)
            if isinstance(value, unicode):
                value = value.encode(TEXT_ENCODING)
            elif isinstance(value, list):
                value = JsonEncoder.json_str_decode_list(value)
            elif isinstance(value, dict):
                value = JsonEncoder.json_str_decode_dict(value)
            rv[key] = value
        return rv


class YamlEncoder(Encoder):
    """YAML encoder for storing HTTP responses in plain text."""

    file_ext = '.yaml'

    def dump(self, data):
        """Return a YAML encoded string of the data."""
        return yaml.dump(data)

    def load(self, encoded_str):
        """Return an object from the encoded JSON string."""
        return yaml.load(encoded_str)


SUPPORTED_FORMATS = {
    'json': JsonEncoder(),
    'yaml': YamlEncoder()
}

DEFAULT_COMPATIBLE_ENCODER = SUPPORTED_FORMATS['yaml']
DEFAULT_ENCODER = SUPPORTED_FORMATS['json']
