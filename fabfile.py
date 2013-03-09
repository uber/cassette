import sys
import urllib2

from fabric.api import local, task
from fabric.colors import magenta, green

from cassette.tests.test_cassette import TEST_URL


@task
def check_test_server():
    """Verify that test server is running."""

    try:
        urllib2.urlopen(TEST_URL)

    except urllib2.URLError:
        print magenta("\nTest server is not running. Run `fab serve_test_server`.")
        sys.exit(1)

from setup import __version__ as current_version


@task
def test(args=""):
    """Run the test suite."""

    check_test_server()
    clean()

    print green("\nRunning tests")

    local("flake8 --ignore=E501,E702 .")
    local("nosetests %s" % args)


@task
def t(args="-x"):
    """Run the test suite in fast mode."""
    test(args)


@task
def clean():
    """Remove all .py[co] files"""
    local("find . -name '*.py[co]' -delete")


@task
def serve_test_server():
    """Start the test server."""
    local("python cassette/tests/server/run.py")


@task
def release():
    """Release a version."""

    test()
    print "Current version is: %s" % current_version
    print "Do the following:"

    steps = (
        "Bump version in setup.py",
        "Run `version='0.1.x'",
        "Run `git status`",
        "Run `git commit -am 'Bump version'`",
        "Run `git tag -a -m 'Version $version' v$version`",
        "Run `git push --tags`",
        "Run `python setup.py register sdist upload`",
    )

    for i, step in enumerate(steps):
        print "%d. %s" % (i, step)
