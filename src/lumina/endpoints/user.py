from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

import lumina.emails.render
import lumina.emails.send
from lumina import auth
from lumina.schema.user import (
    RegisterUserRequest,
    UserPrivateResponse,
    UserPublicResponse,
)

router = APIRouter()


@router.get(
    "/{id}",
    response_model=UserPrivateResponse,
    responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}},
)
def read_user(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    return UserPrivateResponse(id=id, email=auth_user.id)


@router.get(
    "/{id}/check",
    response_model=UserPublicResponse,
    responses={int(HTTPStatus.NOT_FOUND): {"description": "User not found"}},
)
def check_user(id: str):
    raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")


@router.post("/{id}")
def register_user(id: str, new_user: RegisterUserRequest):
    lumina.emails.send.send_email(
        to_addresses=[(new_user.full_name, new_user.email)],
        subject="Finish your registration",
        body=lumina.emails.render.render_email(
            "register_user.html",
            name=new_user.full_name,
            auth_url=auth.get_auth_url(id),
        ),
    ),
    return "OK"


@router.put(
    "/{id}", responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}}
)
def update_user(
    id: str,
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    if id != auth_user.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot update another user"
        )
    ...


@router.delete(
    "/{id}", responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}}
)
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
