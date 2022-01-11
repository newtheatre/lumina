import datetime

from lumina.schema.base import LuminaModel


class AuthCheckResponse(LuminaModel):
    id: str
    expires_at: datetime.datetime
