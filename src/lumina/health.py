import logging
from http import HTTPStatus
from typing import Dict, Tuple

import botocore.exceptions
from github import BadCredentialsException

import lumina.github.connection
from lumina import ssm
from lumina.config import settings
from lumina.database import operations
from lumina.database.operations import ResultNotFound
from lumina.schema.health import HealthCheckCondition, HealthCheckResponse
from lumina.util import dates

log = logging.getLogger(__name__)


def check_ssm() -> HealthCheckCondition:
    try:
        # Check if the SSM service is available by grabbing a known key
        ssm.get_parameter("/lumina/jwt/public")
        return HealthCheckCondition(
            ok=True,
            timestamp=dates.now(),
        )
    except ValueError:
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Parameter not found",
        )
    except botocore.exceptions.ClientError as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="ClientError",
        )
    except Exception as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Unknown error",
        )


def check_dynamodb() -> HealthCheckCondition:
    try:
        # Check if dynamodb is available by attempting fetch of a member
        try:
            operations.get_member("fred_bloggs")
        except ResultNotFound:
            # We don't expect member to exist
            pass
        return HealthCheckCondition(
            ok=True,
            timestamp=dates.now(),
        )
    except botocore.exceptions.ClientError as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="ClientError",
        )
    except Exception as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Unknown error",
        )


def check_github() -> HealthCheckCondition:
    try:
        # Check if GitHub is available by grabbing the content repo
        lumina.github.connection.get_content_repo()
        return HealthCheckCondition(
            ok=True,
            timestamp=dates.now(),
        )
    except BadCredentialsException:
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Bad credentials",
        )
    except botocore.exceptions.ClientError as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Cannot get credentials",
        )
    except Exception as e:
        log.error(e)
        return HealthCheckCondition(
            ok=False,
            timestamp=dates.now(),
            message="Unknown error",
        )


def get_health_check_response() -> Tuple[int, HealthCheckResponse]:
    # To add a new check, add here and to HealthCheckResponse
    results: Dict[str, HealthCheckCondition] = dict(
        check_ssm=check_ssm(),
        check_dynamodb=check_dynamodb(),
        check_github=check_github(),
    )
    body = HealthCheckResponse(version=settings.vcs_rev, **results)
    any_failed = any(condition.ok is False for condition in results.values())
    return (HTTPStatus.INTERNAL_SERVER_ERROR if any_failed else HTTPStatus.OK, body)
