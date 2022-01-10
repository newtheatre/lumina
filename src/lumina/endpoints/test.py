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
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    return {"id": auth_user.id}


@router.get("/auth-optional")
def check_auth_optional(
    auth_user: Optional[auth.AuthenticatedUser] = Depends(
        auth.optional_authenticated_user
    ),
):
    return {"id": auth_user.id if auth_user else None}


@router.get("/auth")
def make_token(
    user_id: str,
):
    # TODO: Remove once we have auth via email
    return auth.encode_jwt(user_id)
