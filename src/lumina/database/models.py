import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from . import table


class BaseDynamoModel(BaseModel):
    pk: str
    sk: str


class MemberConsent(BaseModel):
    consent_news: Optional[datetime.datetime]
    consent_network: Optional[datetime.datetime]
    consent_members: Optional[datetime.datetime]
    consent_students: Optional[datetime.datetime]


class MemberModel(BaseDynamoModel):
    sk = table.SK_PROFILE
    name: str
    email: EmailStr
    phone: Optional[str]
    year_of_graduation: Optional[int]
    created_at: Optional[datetime.datetime]
    consent: Optional[MemberConsent]

    def to_submitter(self) -> "SubmitterModel":
        return SubmitterModel(
            id=self.pk,
            verified=True,
            name=self.name,
            email=self.email,
            year_of_graduation=self.year_of_graduation,
        )


class SubmitterModel(BaseModel):
    id: str
    verified: bool
    name: str
    year_of_graduation: Optional[int]
    email: Optional[EmailStr]


class SubmissionModel(BaseDynamoModel):
    url: str
    target_id: str
    target_type: str
    target_name: str
    message: Optional[str]
    submitter: SubmitterModel

    @property
    def get_issue_id(self) -> int:
        # TODO: Use this when we have Python 3.9
        # return int(self.target_id.removeprefix(f"{table.SK_SUBMISSION}/"))
        return int(self.sk.split("/")[-1])
