from unittest import mock

import pytest
from fixtures import keys


@pytest.fixture()
def mock_keys():
    with mock.patch(
        "lumina.auth.get_jwt_public_key", return_value=keys.EXAMPLE_PUBLIC_KEY
    ), mock.patch(
        "lumina.auth.get_jwt_private_key", return_value=keys.EXAMPLE_PRIVATE_KEY
    ):
        yield
