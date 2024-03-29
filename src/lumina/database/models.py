import datetime
from enum import Enum
from typing import Literal
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from lumina.util.types import BaseModelProtocol
from pydantic import BaseModel, EmailStr

from . import table


class DynamoExportMixin:
    def ddict(self: BaseModelProtocol, **kwargs):
        """dict() export for DynamoDB, removes any Python-only fields, essentially
        JSON but still in dict form"""
        return jsonable_encoder(self.model_dump(**kwargs))


class BaseDynamoModel(BaseModel):
    pk: str
    sk: str


class MemberConsentModel(BaseModel, DynamoExportMixin):
    consent_news: datetime.datetime | None = None
    consent_network: datetime.datetime | None = None
    consent_members: datetime.datetime | None = None
    consent_students: datetime.datetime | None = None


class MemberModel(BaseDynamoModel, DynamoExportMixin):
    sk: Literal["profile"] = table.SK_PROFILE
    name: str
    email: EmailStr
    phone: str | None = None
    year_of_graduation: int | None = None
    created_at: datetime.datetime | None = None
    email_verified_at: datetime.datetime | None = None
    consent: MemberConsentModel | None = None
    anonymous_ids: list[UUID] | None = None
    is_admin: bool = False

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
    year_of_graduation: int | None = None
    email: EmailStr | None = None


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
    closed_at: datetime.datetime | None = None
    comments: int


class SubmissionModel(BaseDynamoModel, DynamoExportMixin):
    url: str
    target_id: str
    target_type: str
    target_name: str
    created_at: datetime.datetime
    subject: str | None = None
    message: str | None = None
    submitter: SubmitterModel
    github_issue: GitHubIssueModel

    @property
    def issue_id(self) -> int:
        try:
            return int(self.sk.removeprefix(table.SK_SUBMISSION_PREFIX))
        except ValueError as e:
            raise ValueError(f"Invalid target_id: {self.sk}, cannot parse int") from e
