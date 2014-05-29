"""
    utils.py

    Helper functions.
"""

TEXT_ENCODING = 'ISO-8859-1'


# JSON Decoding functions (non-unicode)

# Code from stack overflow:
# http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-
# of-unicode-ones-from-json-in-python

def json_str_decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode(TEXT_ENCODING)
        elif isinstance(item, list):
            item = json_str_decode_list(item)
        elif isinstance(item, dict):
            item = json_str_decode_dict(item)
        rv.append(item)
    return rv


def json_str_decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode(TEXT_ENCODING)
        if isinstance(value, unicode):
            value = value.encode(TEXT_ENCODING)
        elif isinstance(value, list):
            value = json_str_decode_list(value)
        elif isinstance(value, dict):
            value = json_str_decode_dict(value)
        rv[key] = value
    return rv
