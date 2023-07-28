from http import HTTPStatus

import lumina.database.operations
import lumina.github
import lumina.github.submissions
from fastapi import APIRouter, Depends, HTTPException
from lumina import auth
from lumina.database.models import MemberModel
from lumina.schema.submissions import (
    BaseSubmissionRequest,
    BioSubmissionRequest,
    GenericSubmissionRequest,
    ShowSubmissionRequest,
    SubmissionResponse,
    SubmissionStatsResponse,
)

router = APIRouter()


@router.get("/member/{id}", response_model=list[SubmissionResponse])
def list_member_submissions(
    id: str,
):
    return [
        SubmissionResponse.from_model(submission)
        for submission in sorted(
            lumina.database.operations.get_submissions_for_member(id),
            key=lambda x: x.created_at,
            reverse=True,
        )
    ]


@router.get("/member/{id}/stats", response_model=SubmissionStatsResponse)
def read_member_submission_stats(
    id: str,
):
    member_submissions = lumina.database.operations.get_submissions_for_member(id)
    return SubmissionStatsResponse(
        count=len(member_submissions),
    )


def require_submitter_or_member(
    submission: BaseSubmissionRequest, member: MemberModel | None
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
    member: MemberModel | None = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    submitter_id = member.pk if member else submission.submitter.id
    issue = lumina.github.submissions.create_generic_submission_issue(
        submission_request=submission, member=member
    )
    submission_instance = lumina.database.operations.put_submission(
        submission.to_model(
            submission_id=issue.number,
            submitter_id=submitter_id,
            member=member,
            github_issue=issue,
        )
    )
    return SubmissionResponse.from_model(submission_instance)


@router.post("/show")
def create_show_submission(
    submission: ShowSubmissionRequest,
    member: MemberModel | None = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    if member:
        return member.id
    return "not authenticated, but it's fine"


@router.post("/bio")
def create_bio_submission(
    submission: BioSubmissionRequest,
    member: MemberModel | None = Depends(auth.optional_member),
):
    require_submitter_or_member(submission, member)
    if member:
        return member.id
    return "not authenticated, but it's fine"
