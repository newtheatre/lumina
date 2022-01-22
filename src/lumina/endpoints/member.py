from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

import lumina.database.operations
import lumina.emails.render
import lumina.emails.send
from lumina import auth
from lumina.schema.member import (
    MemberPrivateResponse,
    MemberPublicResponse,
    RegisterMemberRequest,
)
from lumina.util.email import mask_email

router = APIRouter()


@router.get(
    "/{id}",
    response_model=MemberPrivateResponse,
    responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}},
)
def read_member(
    id: str,
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    return MemberPrivateResponse(id=id, email=member.id)


@router.get(
    "/{id}/check",
    response_model=MemberPublicResponse,
    responses={int(HTTPStatus.NOT_FOUND): {"description": "Member not found"}},
)
def check_member(id: str):
    try:
        member = lumina.database.operations.get_member(id)
        return MemberPublicResponse(id=member.pk, masked_email=mask_email(member.email))
    except lumina.database.operations.ResultNotFound:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Member not found")


@router.post("/{id}")
def register_member(id: str, new_member: RegisterMemberRequest):
    lumina.emails.send.send_email(
        to_addresses=[(new_member.full_name, new_member.email)],
        subject="Finish your registration",
        body=lumina.emails.render.render_email(
            "register_member.html",
            name=new_member.full_name,
            auth_url=auth.get_auth_url(id),
        ),
    ),
    return "OK"


@router.put(
    "/{id}", responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}}
)
def update_member(
    id: str,
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    if id != member.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot update another member"
        )
    ...


@router.delete(
    "/{id}", responses={int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"}}
)
def delete_member(
    id: str,
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    if id != member.id:
        raise HTTPException(status_code=403, detail="You cannot delete another member")
    ...


@router.post("/{id}/verify")
def verify_email(token: str):
    ...


@router.post("/{id}/login")
def send_token_link_for_member(id: str):
    ...