from os import environ
from unittest import mock

import pytest


@pytest.fixture(autouse=True)
def mock_token():
    # To generate VCR cassettes, set the environment variable `GITHUB_TOKEN` to the
    # test access token. This way we can generate test cassettes against the real
    # GitHub API without committing secrets.
    with mock.patch(
        "lumina.github.connection.get_access_token",
        return_value=environ.get("GITHUB_TOKEN"),
    ):
        yield
