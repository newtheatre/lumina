import datetime

from lumina.schema.base import LuminaModel
from pydantic import Field


class HealthCheckCondition(LuminaModel):
    ok: bool = Field(description="Whether the condition is ok")
    timestamp: datetime.datetime = Field(description="When the last check ran")
    message: str | None = Field(description="Details of fault if any")


class HealthCheckResponse(LuminaModel):
    version: str = Field(description="Version of app", example="1.0.0")
    check_ssm: HealthCheckCondition
    check_dynamodb: HealthCheckCondition
    check_github: HealthCheckCondition
