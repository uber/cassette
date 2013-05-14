Quickstart
==========

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
