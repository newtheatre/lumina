import datetime
from typing import Optional

from lumina.schema.base import LuminaModel


class AuthCheckRequiredResponse(LuminaModel):
    id: str
    expires_at: datetime.datetime


class AuthCheckOptionalResponse(LuminaModel):
    id: Optional[str]
    expires_at: Optional[datetime.datetime]
