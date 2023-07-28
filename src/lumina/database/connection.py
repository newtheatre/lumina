import functools

import boto3
from lumina.config import settings
from mypy_boto3_dynamodb import DynamoDBServiceResource


@functools.lru_cache(maxsize=1)
def get_dynamo_db() -> DynamoDBServiceResource:
    return boto3.resource("dynamodb", region_name=settings.aws_region)
