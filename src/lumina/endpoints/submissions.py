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


@router.get("/user/{id}")
def get_user_submissions(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    return auth_user.id


@router.post("/message")
def create_generic_submission(
    submission: GenericSubmissionRequest,
    auth_user: Optional[auth.AuthenticatedUser] = Depends(
        auth.optional_authenticated_user
    ),
):
    if auth_user:
        return auth_user.id
    else:
        return "not authenticated, but it's fine"


@router.post("/show")
def create_show_submission(
    submission: ShowSubmissionRequest,
    auth_user: Optional[auth.AuthenticatedUser] = Depends(
        auth.optional_authenticated_user
    ),
):
    if auth_user:
        return auth_user.id
    else:
        return "not authenticated, but it's fine"


@router.post("/bio")
def create_bio_submission(
    submission: BioSubmissionRequest,
    auth_user: Optional[auth.AuthenticatedUser] = Depends(
        auth.optional_authenticated_user
    ),
):
    if auth_user:
        return auth_user.id
    else:
        return "not authenticated, but it's fine"
