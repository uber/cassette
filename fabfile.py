from fabric.api import local, task


@task
def test(args=""):
    """Run the test suite."""

    clean()
    local("flake8 . --ignore=E501,E702,W806,W402,W802,E128")
    local("nosetests")


@task
def clean():
    """Remove all .pyc files"""

    # Ignore hidden files and folder
    local("find . \( ! -regex '.*/\..*/..*' \) -type f -name '*.pyc' -exec rm '{}' +")
