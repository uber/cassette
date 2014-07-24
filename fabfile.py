from fabric.api import local, task, lcd
from fabric.colors import green

TEST_URL = "http://127.0.0.1:5000/index"


@task
def test(args=""):
    """Run the test suite."""

    clean()

    print green("\nRunning tests")

    local("flake8 --ignore=E501,E702 --exclude=env .")
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
def docs():
    """Generate documentation."""

    local("python setup.py develop")
    with lcd("./docs"):
        local("make html")


@task
def release():
    """Prepare a release."""

    print green("\nRunning prerelease")
    test()
    docs()
    local("prerelease")

    print green("\nReleasing...")
    local("release")
    local("git push --tags")
    local("git push")


@task
def bootstrap():
    """Bootstrap the developer environment."""

    local("pip install -r requirements-dev.txt")
    local("pip install -r requirements.txt")
