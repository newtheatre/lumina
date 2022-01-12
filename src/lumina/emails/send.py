import email.utils
import logging
from typing import List, NamedTuple, Optional, Tuple

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_ses.type_defs import BodyTypeDef, ContentTypeDef, MessageTypeDef

log = logging.getLogger(__name__)

FROM_ADDRESS = email.utils.formataddr(("New Theatre Alumni Network", "nthp@wjdp.uk"))
CHARSET = "UTF-8"


class EmailError(Exception):
    pass


class EmailAddressUnverified(Exception):
    pass


class EmailBody(NamedTuple):
    plaintext: str
    html: str


def send_email(
    to_addresses: List[Tuple[Optional[str], str]],
    subject: str,
    body: EmailBody,
) -> str:
    """
    Send an email via SES.
    :param to_addresses: A list of email addresses to send the email to, tuples in the
                         form (name, email). Name is optional.
    :param subject: The subject of the email.
    :param plaintext: The plaintext body of the email.
    :param html: The HTML body of the email, optional.
    :return: The message ID of the email.
    """
    ses_client = boto3.client("ses")

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = ses_client.send_email(
            Destination={
                "ToAddresses": list(map(email.utils.formataddr, to_addresses)),
            },
            Message=MessageTypeDef(
                Subject=ContentTypeDef(Data=subject, Charset=CHARSET),
                Body=BodyTypeDef(
                    Text=ContentTypeDef(Data=body.plaintext, Charset=CHARSET),
                    Html=ContentTypeDef(Data=body.html, Charset=CHARSET),
                ),
            ),
            Source=FROM_ADDRESS,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        error_message = e.response.get("Error", {}).get("Message", "")
        log.error("Failed to send email: %s", error_message)
        if "Email address not verified" in error_message:
            raise EmailAddressUnverified() from e
        raise EmailError() from e
    else:
        log.info("Email sent, message ID %s", response["MessageId"])
        return response["MessageId"]
