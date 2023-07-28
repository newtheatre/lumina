from os import environ

import pytest

environ["AWS_DEFAULT_REGION"] = "eu-west-2"


@pytest.fixture(scope="module")
def vcr_config():
    return {
        # Remove the Authorization request header
        "filter_headers": [("Authorization", None)],
    }
