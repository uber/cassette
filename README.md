cassette
========

```python
import urllib2

import cassette


def test_get_root_domains():
    """Get the root domains."""

    with cassette.play("data/responses.yaml"):
        r = urllib2.urlopen("http://www.internic.net/domain/named.root")

    assert "A.ROOT-SERVERS.NET" in r.read(10000)
```

* The first time you run your tests, `cassette` will store all the external
  requests response in a YAML file.
* Next time you run your tests, `cassette` will fetch those responses from the
  YAML file. You can now run your tests while being offline.

Installation
============

Locally:

    $ python setup.py develop

Via PyPi:

    $ pip install cassette

Usage
=====

cassette provides a `play` context:

```python
import cassette

with cassette.play("./data/responses.yaml"):
    urllib2.urlopen("http://...")
```

Any `urllib2.urlopen` request happening in this context will go through
cassette's mocked version of `urlopen`.

You can also setup the context manually:

```python
import cassette

cassette.insert("./data/responses.yaml")
urllib2.urlopen("http://...")
cassette.eject()
```

Running casette tests
=====================

    $ paver test

Similar libraries
=================

* [vcrpy](https://github.com/kevin1024/vcrpy): great library but you can store
  only one request per YAML file...
* [vcr](https://github.com/myronmarston/vcr): in Ruby

Limitations
===========

This package should be considered alpha:

* Only tested with `urllib2`
* Should not work with `urllib` and `requests`
* The format used is not compatible with `vcr` or `vcrpy`
* Only tested with Python 2.7

License
=======

cassette is available under the MIT License.
