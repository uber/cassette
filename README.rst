Cassette
========

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
