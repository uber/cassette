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

Report which cassettes are not used
-----------------------------------

.. versionadded:: 0.3.7
   Ability to report which cassettes are not used.

Here's a way to do it:

.. literalinclude:: ../cassette/tests/use_cases/test_report_unused.py

Here's who you would use teardown with pytest to log those unused cassettes
to a file:

.. code:: python

    @pytest.fixture(scope="session", autouse=True)
    def report_unused_cassette(request):
        """Report unused cassettes."""
        def func():
            with open('.unused_cassette.log', 'w') as f:
                cassette_player.report_unused_cassettes(f)
        request.addfinalizer(func)

You would then ``cd`` to the directory containing the fixtures, and run::

    $ xargs rm < ../../../../.unused_cassette.log
