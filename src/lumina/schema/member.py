from pydantic import EmailStr

from lumina.database.models import MemberModel
from lumina.schema.base import LuminaModel


class MemberPublicResponse(LuminaModel):
    id: str
    masked_email: str


class MemberPrivateResponse(LuminaModel):
    id: str
    email: EmailStr
    email_verified: bool

    @classmethod
    def from_model(cls, model: MemberModel):
        return cls(
            id=model.pk,
            email=model.email,
            email_verified=model.email_verified,
        )


class RegisterMemberRequest(LuminaModel):
    full_name: str
    email: EmailStr
