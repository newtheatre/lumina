from http import HTTPStatus
from typing import Optional

from fastapi import APIRouter, Depends

from lumina import auth
from lumina.schema.auth import AuthCheckOptionalResponse, AuthCheckRequiredResponse

router = APIRouter()


@router.get(
    "/check/required",
    response_model=AuthCheckRequiredResponse,
    responses={int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"}},
)
def check_auth(
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    return AuthCheckRequiredResponse(id=member.id, expires_at=member.expires_at)


@router.get("/check/optional", response_model=AuthCheckOptionalResponse)
def check_auth_optional(
    member: Optional[auth.AuthenticatedMember] = Depends(
        auth.optional_authenticated_member
    ),
):
    if member:
        return AuthCheckOptionalResponse(id=member.id, expires_at=member.expires_at)
    else:
        return AuthCheckOptionalResponse()
