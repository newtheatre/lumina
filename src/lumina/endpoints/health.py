from http import HTTPStatus

from fastapi import APIRouter, Response
from lumina import health
from lumina.schema.health import HealthCheckResponse

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
    response.status_code, body = health.get_health_check_response()
    return body
