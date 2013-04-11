Usage
=====

cassette provides a ``play`` context:

.. code:: python

    import cassette

    with cassette.play("./data/responses.yaml"):
        urllib2.urlopen("http://...")

Any ``urllib2.urlopen`` request happening in this context will go
through cassette's mocked version of ``urlopen``.

You can also setup the context manually:

.. code:: python

    import cassette

    cassette.insert("./data/responses.yaml")
    urllib2.urlopen("http://...")
    cassette.eject()
