from fabric.api import task, local


@task
def test():
    """Run the test suite."""
    local("flake8 . --ignore=E501,E702")
    local("nosetests")
