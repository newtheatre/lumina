import datetime
import logging
from http import HTTPStatus
from typing import Dict, Tuple

import botocore.exceptions
from github import BadCredentialsException

from lumina import github, ssm
from lumina.config import settings
from lumina.schema.health import HealthCheckCondition, HealthCheckResponse

log = logging.getLogger(__name__)


def check_ssm() -> HealthCheckCondition:
    try:
        # Check if the SSM service is available by grabbing a known key
        ssm.get_parameter("/lumina/jwt/public")
        return HealthCheckCondition(
            ok=True,
            timestamp=datetime.datetime.now(),
        )
    except ValueError:
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="Parameter not found",
        )
    except botocore.exceptions.ClientError as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="ClientError",
        )
    except Exception as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="Unknown error",
        )


def check_github() -> HealthCheckCondition:
    try:
        # Check if GitHub is available by grabbing the content repo
        github.get_content_repo()
        return HealthCheckCondition(
            ok=True,
            timestamp=datetime.datetime.now(),
        )
    except BadCredentialsException:
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="Bad credentials",
        )
    except botocore.exceptions.ClientError as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="Cannot get credentials",
        )
    except Exception as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="Unknown error",
        )


def get_health_check_response() -> Tuple[int, HealthCheckResponse]:
    results: Dict[str, HealthCheckCondition] = dict(
        check_ssm=check_ssm(),
        check_github=check_github(),
    )
    body = HealthCheckResponse(version=settings.vcs_rev, **results)
    any_failed = any(condition.ok is False for condition in results.values())
    return (HTTPStatus.INTERNAL_SERVER_ERROR if any_failed else HTTPStatus.OK, body)
