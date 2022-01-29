from uuid import UUID

from pydantic import EmailStr, Field

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
    anonymous_id: UUID = Field(
        title="Anonymous ID",
        description="Anonymous ID of the prospective member used to make submissions "
        "before registration.",
    )
    full_name: str = Field(
        title="Full Name",
        description="Full name of the prospective member.",
        example="Fred Bloggs",
    )
    email: EmailStr = Field(
        title="Email",
        description="Email address of the prospective member.",
        example="fred@bloggs.com",
    )
