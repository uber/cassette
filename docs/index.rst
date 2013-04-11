.. Cassette documentation master file, created by
   sphinx-quickstart on Thu Apr 11 10:52:01 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Cassette's documentation!
====================================

Cassette stores and replays HTTP requests made in your Python app.

Latest documentation: `uber.github.io/cassette/ <http://uber.github.io/cassette/>`_

Contents
--------

.. toctree::
   :maxdepth: 2

   usage
   api
   development


Quickstart
----------

*  The first time you run your tests, ``cassette`` will store all the
   external requests response in a YAML file.
*  Next time you run your tests, ``cassette`` will fetch those responses
   from the YAML file. You can now run your tests while being offline.

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


Similar libraries
-----------------

-  `vcrpy <https://github.com/kevin1024/vcrpy>`__: great library but you
   can store only one request per YAML file...
-  `vcr <https://github.com/myronmarston/vcr>`__: in Ruby

Limitations
-----------

This package should be considered **alpha**:

-  Only tested with ``urllib2``
-  Should not work with ``urllib`` and ``requests``
-  The format used is not compatible with ``vcr`` or ``vcrpy``
-  Only tested with Python 2.7
-  File format **WILL** change.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
