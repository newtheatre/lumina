from datetime import datetime
from uuid import UUID

from lumina.database.models import MemberConsentModel, MemberModel
from lumina.schema.base import LuminaModel
from lumina.util import dates
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
            consent_news=model.consent_news is not None,
            consent_network=model.consent_network is not None,
            consent_members=model.consent_members is not None,
            consent_students=model.consent_students is not None,
        )

    @classmethod
    def get_no_consent(cls):
        return cls(
            consent_news=False,
            consent_network=False,
            consent_members=False,
            consent_students=False,
        )

    def to_model(self):
        consent = lambda x: dates.now() if x else None  # noqa: E731
        return MemberConsentModel(
            consent_news=consent(self.consent_news),
            consent_network=consent(self.consent_network),
            consent_members=consent(self.consent_members),
            consent_students=consent(self.consent_students),
        )


class MemberPrivateResponse(LuminaModel):
    id: str
    created_at: datetime | None
    email: EmailStr
    email_verified: bool
    email_verified_at: datetime | None
    phone: str | None
    year_of_graduation: int | None
    consent: MemberConsent
    anonymous_ids: list[UUID] | None

    @classmethod
    def from_model(cls, model: MemberModel):
        return cls(
            id=model.pk,
            created_at=model.created_at,
            email=model.email,
            email_verified=model.email_verified,
            email_verified_at=model.email_verified_at,
            phone=model.phone,
            year_of_graduation=model.year_of_graduation,
            consent=MemberConsent.from_model(model.consent)
            if model.consent
            else MemberConsent.get_no_consent(),
            anonymous_ids=model.anonymous_ids,
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
    year_of_graduation: int | None = Field(
        title="Year of Graduation",
        description="Year of graduation of the prospective member, "
        "leave blank if unknown.",
        example=2021,
    )
    consent: MemberConsent = Field(
        title="Consent",
        description="Consent of the prospective member for use of their data.",
    )

    def to_model(self, id: str) -> MemberModel:
        return MemberModel(
            pk=id,
            name=self.full_name,
            email=self.email,
            anonymous_ids=[self.anonymous_id],
            year_of_graduation=self.year_of_graduation,
            consent=self.consent.to_model(),
        )


class UpdateMemberRequest(LuminaModel):
    phone: str | None
    consent: MemberConsent = Field(
        title="Consent",
        description="Changes to consent options for the member.",
    )
