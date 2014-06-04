Usage
=====

cassette provides a ``play`` context:

.. code:: python

    import cassette

    with cassette.play("./data/responses.yaml"):
        urllib2.urlopen("http://...")

You can also setup the context manually:

.. code:: python

    import cassette

    cassette.insert("./data/responses.yaml")
    urllib2.urlopen("http://...")
    cassette.eject()

Storage backend
---------------

.. versionadded:: 0.3.1
   Ability to read from a directory.

.. versionadded:: 0.3.1
   Ability to read from JSON files.

cassette supports multiple storage backend:

* File based (all the requests and responses are in the same file)
* Directory based (each request/response is in a single file)

Two formats are supported, JSON (faster) and YAML.

To read from a directory, just provide the path:

.. code:: python

    cassette.insert("./data/", file_format="json")
