from http import HTTPStatus

from fastapi import APIRouter, Depends
from lumina import auth
from lumina.database.models import MemberModel
from lumina.schema.auth import AuthCheckOptionalResponse, AuthCheckRequiredResponse

router = APIRouter()


@router.get(
    "/check/required",
    response_model=AuthCheckRequiredResponse,
    responses={int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"}},
)
def check_auth(
    token: auth.AuthenticatedToken = Depends(auth.JWTBearer(optional=False)),
    member: MemberModel = Depends(auth.require_member),
):
    return AuthCheckRequiredResponse(id=member.id, expires_at=token.expires_at)


@router.get(
    "/check/optional",
    response_model=AuthCheckOptionalResponse,
    responses={
        int(HTTPStatus.UNAUTHORIZED): {"description": "Member no longer exists"}
    },
)
def check_auth_optional(
    token: auth.AuthenticatedToken = Depends(auth.JWTBearer(optional=True)),
    member: MemberModel | None = Depends(auth.optional_member),
):
    if member:
        return AuthCheckOptionalResponse(id=member.id, expires_at=token.expires_at)
    else:
        return AuthCheckOptionalResponse()
