from uuid import UUID

from lumina.database.models import MemberConsentModel, MemberModel
from lumina.schema.base import LuminaModel
from pydantic import EmailStr, Field


class MemberPublicResponse(LuminaModel):
    id: str
    masked_email: str


class MemberConsent(LuminaModel):
    consent_news: bool
    consent_network: bool
    consent_members: bool
    consent_students: bool

    @classmethod
    def from_model(cls, model: MemberConsentModel):
        return cls(
            consent_news=model.consent_news,
            consent_network=model.consent_network,
            consent_members=model.consent_members,
            consent_students=model.consent_students,
        )

    @classmethod
    def get_no_consent(cls):
        return cls(
            consent_news=False,
            consent_network=False,
            consent_members=False,
            consent_students=False,
        )


class MemberPrivateResponse(LuminaModel):
    id: str
    email: EmailStr
    email_verified: bool
    consent: MemberConsent

    @classmethod
    def from_model(cls, model: MemberModel):
        return cls(
            id=model.pk,
            email=model.email,
            email_verified=model.email_verified,
            consent=MemberConsent.from_model(model.consent)
            if model.consent
            else MemberConsent.get_no_consent(),
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
