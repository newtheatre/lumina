from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

import lumina.database.operations
import lumina.github
from lumina import auth
from lumina.database.models import MemberModel
from lumina.schema.submissions import (
    BaseSubmissionRequest,
    BioSubmissionRequest,
    GenericSubmissionRequest,
    ShowSubmissionRequest,
    SubmissionResponse,
)

router = APIRouter()


@router.get("/member/{id}")
def get_member_submissions(
    id: str,
    member: MemberModel = Depends(auth.require_member),
):
    return member.id


def require_submitter_or_member(
    submission: BaseSubmissionRequest, member: Optional[MemberModel]
):
    if not (submission.submitter or member):
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="You must either provide a submitter or authenticate as a member",
        )
    if submission.submitter and member:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail="You must not provide a submitter if you are authenticated",
        )


@router.post(
    "/message",
    description="Create a generic submission, a 'message the editors' type thing.",
    response_model=SubmissionResponse,
)
def create_generic_submission(
    submission: GenericSubmissionRequest,
    member: Optional[MemberModel] = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    submitter_id = member.pk if member else submission.submitter.id
    issue = lumina.github.create_generic_submission_issue(
        submission_request=submission, member=member
    )
    submission_instance = lumina.database.operations.put_submission(
        submission.to_model(
            submission_id=issue.number, submitter_id=submitter_id, member=member
        )
    )
    return SubmissionResponse.from_model(submission_instance, issue)


@router.post("/show")
def create_show_submission(
    submission: ShowSubmissionRequest,
    member: Optional[MemberModel] = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    if member:
        return member.id
    else:
        return "not authenticated, but it's fine"


@router.post("/bio")
def create_bio_submission(
    submission: BioSubmissionRequest,
    member: Optional[MemberModel] = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    if member:
        return member.id
    else:
        return "not authenticated, but it's fine"
