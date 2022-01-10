from fastapi import APIRouter, Depends, HTTPException

from lumina import auth
from lumina.schema.user import (
    RegisterUserRequest,
    UserPrivateResponse,
    UserPublicResponse,
)

router = APIRouter()


@router.get("/{id}", response_model=UserPrivateResponse)
def read_user(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    return UserPrivateResponse(id=id, email=auth_user.id)


@router.get("/{id}/check", response_model=UserPublicResponse)
def check_user(id: str):
    ...


@router.post(
    "/",
)
def register_user(new_user: RegisterUserRequest):
    ...


@router.put("/{id}", responses={403: {"description": "Forbidden"}})
def update_user(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    if id != auth_user.id:
        raise HTTPException(status_code=403, detail="You cannot update another user")
    ...


@router.delete("/{id}", responses={403: {"description": "Forbidden"}})
def delete_user(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    if id != auth_user.id:
        raise HTTPException(status_code=403, detail="You cannot delete another user")
    ...


@router.post("/{id}/verify")
def verify_email(token: str):
    ...


@router.post("/{id}/login")
def send_token_link_for_user(id: str):
    ...
