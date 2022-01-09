from mangum import Mangum

from lumina.app import app

handler = Mangum(app)
