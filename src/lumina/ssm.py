import functools

import boto3


@functools.lru_cache
def get_parameter(name: str) -> str:
    ssm_client = boto3.client("ssm")
    try:
        response = ssm_client.get_parameter(Name=name, WithDecryption=True)
    except ssm_client.exceptions.ParameterNotFound as e:
        raise ValueError(f"Parameter {name} not found") from e
    return response["Parameter"]["Value"]
