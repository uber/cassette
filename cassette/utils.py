"""
    utils.py

    Helper functions.
"""
import yaml
import json

TEXT_ENCODING = 'ISO-8859-1'


class Encoder(object):
    """
        Some DOCSTRING HERE
    """

    file_ext = '.file'

    def dump(self, data):
        raise NotImplementedError('Encoder not implemented.')

    def load(self, encoded_str):
        raise NotImplementedError('Encoder not implemented.')


class JsonEncoder(Encoder):
    """
        More DOCSTRING HERE
    """

    file_ext = '.json'

    def dump(self, data):
        return json.dumps(data, ensure_ascii=False)

    def load(self, encoded_str):
        return json.loads(encoded_str, TEXT_ENCODING,
                          object_hook=JsonEncoder.json_str_decode_dict)

    @staticmethod
    def json_str_decode_list(data):
        # JSON Decoding functions (non-unicode)

        # Code from stack overflow:
        # http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-
        # of-unicode-ones-from-json-in-python
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
    """
        More DOCSTRING HERE
    """

    file_ext = '.yaml'

    def dump(self, data):
        return yaml.dump(data)

    def load(self, encoded_str):
        return yaml.load(encoded_str)
