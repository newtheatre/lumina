import functools

import boto3
from mypy_boto3_dynamodb import DynamoDBServiceResource


@functools.lru_cache(maxsize=1)
def get_dynamo_db() -> DynamoDBServiceResource:
    return boto3.resource("dynamodb", endpoint_url=None)
