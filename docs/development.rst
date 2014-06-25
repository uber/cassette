Development
===========

Running cassette tests
----------------------

The quick and dirty way to run tests is through setup.py:

::

    $ python setup.py test

For more involved development, you can create a virtual environment, install
fabric (``pip install fabric``) then install requirements:

::

    $ fab bootstrap

Start the test server and run tests:

::

    $ fab test

Tests spin up a test server to bounce requests off of, but you can run this
server manually:

::

    $ fab serve_test_server

You will see an error about the test server's address being in use, but this is
harmless.
