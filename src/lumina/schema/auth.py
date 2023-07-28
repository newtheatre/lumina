import datetime

from lumina.schema.base import LuminaModel


class AuthCheckRequiredResponse(LuminaModel):
    id: str
    expires_at: datetime.datetime


class AuthCheckOptionalResponse(LuminaModel):
    id: str | None
    expires_at: datetime.datetime | None
