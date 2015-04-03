import logging

import pytest


@pytest.fixture(scope="session", autouse=True)
def smtp(request):
    logger = logging.getLogger('cassette')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(logging.StreamHandler())
