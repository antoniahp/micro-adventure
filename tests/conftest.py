import pytest


@pytest.fixture(autouse=True)
def _no_rate_limit(settings):
    """The functional tests call the same endpoint many times on purpose; that is not what they are testing."""
    settings.RATE_LIMIT_ENABLED = False
