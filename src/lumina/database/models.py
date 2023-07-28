import datetime
from enum import Enum
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from lumina.util.types import BaseModelProtocol
from pydantic import BaseModel, EmailStr

from . import table


class DynamoExportMixin:
    def ddict(self: BaseModelProtocol, **kwargs):
        """dict() export for DynamoDB, removes any Python-only fields, essentially
        JSON but still in dict form"""
        return jsonable_encoder(self.dict(**kwargs))


class BaseDynamoModel(BaseModel):
    pk: str
    sk: str


class MemberConsent(BaseModel, DynamoExportMixin):
    consent_news: datetime.datetime | None
    consent_network: datetime.datetime | None
    consent_members: datetime.datetime | None
    consent_students: datetime.datetime | None


class MemberModel(BaseDynamoModel, DynamoExportMixin):
    sk = table.SK_PROFILE
    name: str
    email: EmailStr
    phone: str | None
    year_of_graduation: int | None
    created_at: datetime.datetime | None
    email_verified_at: datetime.datetime | None
    consent: MemberConsent | None
    anonymous_ids: list[UUID] | None

    @property
    def id(self) -> str:
        return self.pk

    @property
    def email_verified(self) -> bool:
        return self.email_verified_at is not None

    def to_submitter(self) -> "SubmitterModel":
        return SubmitterModel(
            id=self.pk,
            verified=True,
            name=self.name,
            email=self.email,
            year_of_graduation=self.year_of_graduation,
        )


class SubmitterModel(BaseModel, DynamoExportMixin):
    id: str
    verified: bool
    name: str
    year_of_graduation: int | None
    email: EmailStr | None


class GitHubIssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"
    COMPLETED = "completed"


class GitHubIssueModel(BaseModel, DynamoExportMixin):
    number: int
    state: GitHubIssueState
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed_at: datetime.datetime | None
    comments: int


class SubmissionModel(BaseDynamoModel, DynamoExportMixin):
    url: str
    target_id: str
    target_type: str
    target_name: str
    created_at: datetime.datetime
    subject: str | None
    message: str | None
    submitter: SubmitterModel
    github_issue: GitHubIssueModel

    @property
    def issue_id(self) -> int:
        # TODO: Use this when we have Python 3.9
        return int(self.sk.split("/")[-1])
