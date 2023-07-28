import boto3
import moto
import pytest
from lumina.emails.send import (
    FROM_ADDRESS,
    EmailAddressUnverified,
    EmailBody,
    send_email,
)


class TestSendEmail:
    @moto.mock_ses
    def test_success(self):
        ses_client = boto3.client("ses")
        to_address = "test@example.com"
        ses_client.verify_email_identity(EmailAddress=FROM_ADDRESS)
        send_email(
            [(None, to_address)],
            "Test Subject",
            EmailBody(plaintext="Hello World", html="<p>Hello World</p>"),
        )

    @moto.mock_ses
    def test_unverified_email(self):
        to_address = "test@example.com"
        with pytest.raises(EmailAddressUnverified):
            send_email(
                [(None, to_address)],
                "Test Subject",
                EmailBody(plaintext="Hello World", html="<p>Hello World</p>"),
            )
