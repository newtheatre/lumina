from sentry import init_sentry

# Initialize Sentry, want to do as early as possible
init_sentry()
from lumina.app import app
from mangum import Mangum

handler = Mangum(app)
