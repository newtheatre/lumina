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


class SubmissionSubmitter(BaseModel):
    name: str
    graduation_year: Optional[int]
    email: Optional[EmailStr]


class SubmissionModel(BaseDynamoModel):
    url: str
    target_id: str
    target_type: str
    target_name: str
    message: str
    submitter: Optional[SubmissionSubmitter]
