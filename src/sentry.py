import sentry_sdk
from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

from lumina.config import settings


def init_sentry():
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[AwsLambdaIntegration()],
        traces_sample_rate=1.0,  # adjust the sample rate in production as needed
        environment=settings.environment,
        release=settings.vcs_rev,
        send_default_pii=True,
    )
