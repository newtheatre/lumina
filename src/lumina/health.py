import datetime

import botocore.exceptions

from lumina import ssm
from lumina.schema.health import HealthCheckCondition


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
    except botocore.exceptions.ClientError:
        return HealthCheckCondition(
            ok=False,
            timestamp=datetime.datetime.now(),
            message="ClientError",
        )
