from http import HTTPStatus
from typing import Dict

from fastapi import APIRouter, Response

from lumina import health
from lumina.config import settings
from lumina.schema.health import HealthCheckCondition, HealthCheckResponse

router = APIRouter()


@router.get(
    "",
    response_model=HealthCheckResponse,
    responses={
        int(HTTPStatus.INTERNAL_SERVER_ERROR): {
            "model": HealthCheckResponse,
            "description": "One or more checks failed",
        }
    },
    description="Check the health of the service",
)
def health_check(response: Response):
    results: Dict[str, HealthCheckCondition] = dict(
        check_ssm=health.check_ssm(),
    )
    body = HealthCheckResponse(version=settings.vcs_rev, **results)
    any_failed = any(condition.ok is False for condition in results.values())
    if any_failed:
        response.status_code = HTTPStatus.INTERNAL_SERVER_ERROR
    return body
