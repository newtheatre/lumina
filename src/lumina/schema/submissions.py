from typing import Optional

from lumina.schema.base import LuminaModel


class SubmitterRequest(LuminaModel):
    member_id: Optional[str]
    member_name: str
    member_graduated: Optional[str]


class GenericSubmissionRequest(LuminaModel):
    submitter: SubmitterRequest

    target_type: str
    target_id: str
    target_name: str
    target_url: str
    message: str


class ShowSubmissionRequest(LuminaModel):
    submitter: SubmitterRequest
    target_id: Optional[str]
    title: str


class BioSubmissionRequest(LuminaModel):
    submitter: SubmitterRequest
    target_id: Optional[str]
    name: str
