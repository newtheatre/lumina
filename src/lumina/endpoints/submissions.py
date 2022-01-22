from typing import Optional

from fastapi import APIRouter, Depends

from lumina import auth
from lumina.config import settings
from lumina.schema.submissions import (
    BioSubmissionRequest,
    GenericSubmissionRequest,
    ShowSubmissionRequest,
)

router = APIRouter()


@router.get("/member/{id}")
def get_member_submissions(
    id: str,
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    return member.id


@router.post("/message")
def create_generic_submission(
    submission: GenericSubmissionRequest,
    member: Optional[auth.AuthenticatedMember] = Depends(
        auth.optional_authenticated_member
    ),
):
    if member:
        return member.id
    else:
        return "not authenticated, but it's fine"


@router.post("/show")
def create_show_submission(
    submission: ShowSubmissionRequest,
    member: Optional[auth.AuthenticatedMember] = Depends(
        auth.optional_authenticated_member
    ),
):
    if member:
        return member.id
    else:
        return "not authenticated, but it's fine"


@router.post("/bio")
def create_bio_submission(
    submission: BioSubmissionRequest,
    member: Optional[auth.AuthenticatedMember] = Depends(
        auth.optional_authenticated_member
    ),
):
    if member:
        return member.id
    else:
        return "not authenticated, but it's fine"
