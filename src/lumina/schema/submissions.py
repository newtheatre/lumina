from typing import Optional, Union
from uuid import UUID

from github import Issue
from pydantic import EmailStr, Field

from lumina import github
from lumina.database.models import MemberModel, SubmissionModel, SubmitterModel
from lumina.database.table import get_submission_sk
from lumina.schema.base import LuminaModel

FIELD_SUBMITTER_ID = Field(description="The ID of the submitter", example="fred_bloggs")
FIELD_SUBMITTER_NAME = Field(
    description="The name of the submitter", example="Fred Bloggs"
)


class SubmitterRequest(LuminaModel):
    id: UUID = FIELD_SUBMITTER_ID
    name: str = FIELD_SUBMITTER_NAME
    year_of_graduation: Optional[int] = Field(example=1999)
    email: Optional[EmailStr] = Field(example="fred@bloggs.com")

    def to_model(self) -> SubmitterModel:
        return SubmitterModel(
            id=str(self.id),
            verified=False,
            name=self.name,
            year_of_graduation=self.year_of_graduation,
            email=self.email,
        )


class SubmitterResponse(LuminaModel):
    id: str = FIELD_SUBMITTER_ID
    verified: bool = Field(
        description="Was this submission made by a verified member", example=True
    )
    name: str = FIELD_SUBMITTER_NAME


class BaseSubmissionRequest(LuminaModel):
    submitter: Optional[SubmitterRequest] = Field(
        description="The submitter of the submission if, and only if, the submission "
        "is anonymous. If the user is logged in this field should be omitted.",
    )


FIELD_TARGET_TYPE = Field(
    title="Target Type", description="The type of the target", example="show"
)
FIELD_TARGET_ID = Field(
    title="Target ID",
    description="The ID of the target",
    example="00_01/romeo_and_juliet",
)
FIELD_TARGET_NAME = Field(
    title="Target Name",
    description="The current name of the target",
    example="Romeo and Juliet",
)
FIELD_TARGET_URL = Field(
    title="Target URL",
    description="The URL this submission is being made from",
    example="https://history.newtheatre.org.uk/00_01/romeo_and_juliet",
)
FIELD_MESSAGE = Field(
    title="Message",
    description="The message to be submitted verbatim from the user",
    example="I did the lighting for the show",
)


class GenericSubmissionRequest(BaseSubmissionRequest):
    target_type: str = FIELD_TARGET_TYPE
    target_id: str = FIELD_TARGET_ID
    target_name: str = FIELD_TARGET_NAME
    target_url: str = FIELD_TARGET_URL
    subject: Optional[str] = Field(
        description="The subject of the submission", example="The lighting"
    )
    message: str = FIELD_MESSAGE

    def to_model(
        self,
        *,
        submission_id: int,
        submitter_id: Union[str, UUID],
        member: Optional[MemberModel],
    ) -> SubmissionModel:
        return SubmissionModel(
            pk=str(submitter_id),
            sk=get_submission_sk(submission_id),
            url=self.target_url,
            target_id=self.target_id,
            target_type=self.target_type,
            target_name=self.target_name,
            message=self.message,
            submitter=member.to_submitter() if member else self.submitter.to_model(),
        )


class ShowSubmissionRequest(BaseSubmissionRequest):
    target_id: Optional[str] = FIELD_TARGET_ID
    title: str


class BioSubmissionRequest(BaseSubmissionRequest):
    target_id: Optional[str] = FIELD_TARGET_ID
    name: str


class GitHubIssueResponse(LuminaModel):
    number: int
    url: str
    state: str


class SubmissionResponse(LuminaModel):
    id: int
    submitter: SubmitterResponse = Field(
        description="The submitter of the submission",
    )
    target_type: str = FIELD_TARGET_TYPE
    target_id: str = FIELD_TARGET_ID
    target_name: str = FIELD_TARGET_NAME
    target_url: str = FIELD_TARGET_URL
    message: Optional[str] = FIELD_MESSAGE
    github_issue: GitHubIssueResponse = Field(
        title="GitHub Issue", description="Linked GitHub issue"
    )

    @classmethod
    def from_model(
        cls,
        submission: SubmissionModel,
    ) -> "SubmissionResponse":
        return cls(
            id=submission.issue_id,
            submitter=SubmitterResponse(
                id=submission.pk,
                verified=submission.submitter.verified,
                name=submission.submitter.name,
            ),
            target_type=submission.target_type,
            target_id=submission.target_id,
            target_name=submission.target_name,
            target_url=submission.url,
            message=submission.message,
            github_issue=GitHubIssueResponse(
                number=submission.issue_id,
                url=github.get_content_repo_issue_url(submission.issue_id),
                state="unknown",  # TODO: get state from db
            ),
        )


class SubmissionStatsResponse(LuminaModel):
    count: int = Field(description="The number of submissions")
