from typing import Optional

from fastapi import APIRouter, Depends

from lumina import auth
from lumina.config import settings

router = APIRouter()


@router.get("/hello")
def hello_world():
    return {"Hello": "World"}


@router.get("/config")
def get_config():
    return settings.dict()


@router.get("/auth-required")
def check_auth_required(
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    return {"id": member.id}


@router.get("/auth-optional")
def check_auth_optional(
    member: Optional[auth.AuthenticatedMember] = Depends(
        auth.optional_authenticated_member
    ),
):
    return {"id": member.id if member else None}


@router.get("/auth")
def make_token(
    id: str,
):
    # TODO: Remove once we have auth via email
    return auth.encode_jwt(id)
