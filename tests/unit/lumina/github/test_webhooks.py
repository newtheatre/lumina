from unittest import mock

import fixtures.github
import pytest

from lumina.github import webhooks


@pytest.fixture(autouse=True)
def mock_webhook_secret():
    with mock.patch(
        "lumina.github.webhooks.get_webhook_secret",
        return_value=fixtures.github.SIGNED_SECRET,
    ):
        yield


class TestVerifyWebhook:
    def test_valid(self):
        assert (
            webhooks.verify_webhook(
                signature=fixtures.github.SIGNED_HEADER,
                body=fixtures.github.SIGNED_BODY.encode(),
            )
            is True
        )

    def test_invalid(self):
        assert (
            webhooks.verify_webhook(
                signature=fixtures.github.SIGNED_HEADER,
                body=(fixtures.github.SIGNED_BODY + "a").encode(),
            )
            is False
        )
