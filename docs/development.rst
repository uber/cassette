Development
===========

Running cassette tests
----------------------

Create a virtual environment, install fabric (``pip install fabric``) then
install requirements:

::

    $ fab bootstrap

Start the test server and run tests:

::

    $ fab serve_test_server
    $ fab test
