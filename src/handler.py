from sentry import init_sentry

# Initialize Sentry, want to do as early as possible
init_sentry()
from mangum import Mangum

from lumina.app import app

handler = Mangum(app)
