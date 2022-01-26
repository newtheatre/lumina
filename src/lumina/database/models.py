import datetime
from enum import Enum
from typing import Optional

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, EmailStr
from unit.lumina.util.types import BaseModelProtocol

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
    consent_news: Optional[datetime.datetime]
    consent_network: Optional[datetime.datetime]
    consent_members: Optional[datetime.datetime]
    consent_students: Optional[datetime.datetime]


class MemberModel(BaseDynamoModel, DynamoExportMixin):
    sk = table.SK_PROFILE
    name: str
    email: EmailStr
    phone: Optional[str]
    year_of_graduation: Optional[int]
    created_at: Optional[datetime.datetime]
    email_verified_at: Optional[datetime.datetime]
    consent: Optional[MemberConsent]

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
    year_of_graduation: Optional[int]
    email: Optional[EmailStr]


class GitHubIssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class GitHubIssueModel(BaseModel, DynamoExportMixin):
    number: int
    state: GitHubIssueState
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed_at: Optional[datetime.datetime]
    comments: int


class SubmissionModel(BaseDynamoModel, DynamoExportMixin):
    url: str
    target_id: str
    target_type: str
    target_name: str
    created_at: datetime.datetime
    message: Optional[str]
    submitter: SubmitterModel
    github_issue: GitHubIssueModel

    @property
    def issue_id(self) -> int:
        # TODO: Use this when we have Python 3.9
        # return int(self.target_id.removeprefix(f"{table.SK_SUBMISSION}/"))
        return int(self.sk.split("/")[-1])
