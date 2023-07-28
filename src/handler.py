from sentry import init_sentry

# Initialize Sentry, want to do as early as possible
init_sentry()

from lumina.app import app  # noqa: E402
from mangum import Mangum  # noqa: E402

handler = Mangum(app)
