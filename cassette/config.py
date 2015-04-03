class Config(dict):

    def __init__(self):
        # Defaults
        self['log_cassette_used'] = False
        self['only_recorded'] = False
        self['hash_body'] = True
        self['hash_include_headers'] = True
