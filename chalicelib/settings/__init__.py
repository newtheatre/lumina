import os


class SettingsError(Exception):
    ...


# if not 'STAGE' in os.environ:
#     raise SettingsError("Missing variable STAGE in environment")

STAGE_DEV = 'dev'
STAGE_STAGING = 'staging'
STAGE_PROD = 'prod'

STAGES = [
    STAGE_DEV,
    STAGE_STAGING,
    STAGE_PROD,
]

STAGE: str = os.environ.get('STAGE', 'unknown')

# if STAGE not in STAGES:
#     raise SettingsError(f"Stage '{STAGE}' not a valid stage")

from .common import *

if STAGE == STAGE_DEV:
    from .dev import *
if STAGE == STAGE_STAGING:
    from .staging import *
if STAGE == STAGE_PROD:
    from .prod import *
