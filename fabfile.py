from fabric.api import local, task

from setup import __version__ as current_version


@task
def test(args=""):
    """Run the test suite."""

    clean()
    local("flake8 --ignore=E501,E702 .")
    local("nosetests %s" % args)


@task
def clean():
    """Remove all .pyc files"""

    # Ignore hidden files and folder
    local("find . \( ! -regex '.*/\..*/..*' \) -type f -name '*.pyc' -exec rm '{}' +")


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
