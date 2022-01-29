import datetime
from typing import Optional

from pydantic import Field

from lumina.schema.base import LuminaModel


class HealthCheckCondition(LuminaModel):
    ok: bool = Field(description="Whether the condition is ok")
    timestamp: datetime.datetime = Field(description="When the last check ran")
    message: Optional[str] = Field(description="Details of fault if any")


class HealthCheckResponse(LuminaModel):
    version: str = Field(description="Version of app", example="1.0.0")
    check_ssm: HealthCheckCondition
    check_dynamodb: HealthCheckCondition
    check_github: HealthCheckCondition
    # check_ses: HealthCheckCondition # TODO: implement ses health check
