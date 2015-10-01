Cassette
========

**Deprecation Warning**: cassette has some known limitations and is not maintained anymore, we recommend using `vcrpy <https://github.com/kevin1024/vcrpy>`_ instead.

.. image::  https://img.shields.io/pypi/v/cassette.svg

Cassette stores and replays HTTP requests made in your Python app.

.. code:: python

    import urllib2

    import cassette

    with cassette.play("data/responses.yaml"):

        # If the request is not already stored in responses.yaml, cassette
        # will request the URL and store its response in the file.
        r = urllib2.urlopen("http://www.internic.net/domain/named.root")

        # This time, the request response must be in the file. The external
        # request is not made. cassette retrieves the response from the
        # file.
        r = urllib2.urlopen("http://www.internic.net/domain/named.root")

    assert "A.ROOT-SERVERS.NET" in r.read(10000)

Cassette also supports the `requests <https://github.com/kennethreitz/requests>`_
library.

.. code:: python

    import requests

    with cassette.play("data/responses.yaml"):
        r = requests.get("http://www.internic.net/domain/named.root")

Note that requests stored between different libraries may not be compatible with
each other. That is, a request stored with ``urllib2`` might still trigger an external
request is the same URL is requested with ``requests``.


Installation
------------

.. code-block:: sh

    $ pip install cassette


Documentation
-------------

Latest documentation: `cassette.readthedocs.org <http://cassette.readthedocs.org/>`_


License
-------

cassette is available under the MIT License.

Copyright Uber 2013, Charles-Axel Dein <charles@uber.com>
