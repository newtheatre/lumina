import pytest


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Remove the Authorization request header
        "filter_headers": [("Authorization", None)],
    }
