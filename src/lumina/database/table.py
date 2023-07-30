import functools
from typing import Literal

from lumina.config import settings
from lumina.database.connection import get_dynamo_db
from mypy_boto3_dynamodb.service_resource import Table

MEMBER_TABLE_NAME_PREFIX = "LuminaMember"


def get_table_name() -> str:
    """
    Get the name of the table, this is used in testing and locally.
    On AWS, this is done by the SAM template where the **definitions are duplicated**.
    """
    return f"{MEMBER_TABLE_NAME_PREFIX}-{settings.environment}"


@functools.lru_cache
def get_member_table() -> Table:
    return get_dynamo_db().Table(get_table_name())


MEMBER_PARTITION_KEY = "pk"
MEMBER_SORT_KEY = "sk"

SK_PROFILE: Literal["profile"] = "profile"
SK_SUBMISSION_PREFIX = "submission/"
PK_ANONYMOUS = "ANONYMOUS"

GSI_SK = "gsi_sk"

GSI_SUBMISSION_TARGET = "gsi_submission_target"
GSI_SUBMISSION_TARGET_PK = "target_type"
GSI_SUBMISSION_TARGET_SK = "target_id"


def get_submission_sk(submission_id: int) -> str:
    """Get the sort key for a submission id, the id is a GitHub issue id"""
    return f"{SK_SUBMISSION_PREFIX}{submission_id}"


def create_tables():
    """
    Create the tables for the database, this is used in testing and locally.
    On AWS, this is done by the SAM template where the **definitions are duplicated**.
    """
    return get_dynamo_db().create_table(
        TableName=get_table_name(),
        KeySchema=[
            {"AttributeName": MEMBER_PARTITION_KEY, "KeyType": "HASH"},
            {"AttributeName": MEMBER_SORT_KEY, "KeyType": "RANGE"},
        ],
        AttributeDefinitions=[
            # Only attributes used in indexes should be defined here.
            # It'll crash if you don't use them in an index.
            {"AttributeName": MEMBER_PARTITION_KEY, "AttributeType": "S"},
            {"AttributeName": MEMBER_SORT_KEY, "AttributeType": "S"},
            {"AttributeName": GSI_SUBMISSION_TARGET_PK, "AttributeType": "S"},
            {"AttributeName": GSI_SUBMISSION_TARGET_SK, "AttributeType": "S"},
        ],
        GlobalSecondaryIndexes=[
            # Used to query on sort keys, e.g. getting submission by ID
            {
                "IndexName": GSI_SK,
                "KeySchema": [{"AttributeName": MEMBER_SORT_KEY, "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            },
            # Used to query for submissions by target type and target id
            {
                "IndexName": GSI_SUBMISSION_TARGET,
                "KeySchema": [
                    {"AttributeName": GSI_SUBMISSION_TARGET_PK, "KeyType": "HASH"},
                    {"AttributeName": GSI_SUBMISSION_TARGET_SK, "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            },
        ],
        BillingMode="PAY_PER_REQUEST",
    )
