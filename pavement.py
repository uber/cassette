import os

from paver.easy import task


@task
def test():
    """Run the test suite."""
    os.system("flake8 . --ignore=E501,E702")
    os.system("nosetests")
