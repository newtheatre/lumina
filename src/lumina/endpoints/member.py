from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

import lumina.database.operations
import lumina.emails.render
import lumina.emails.send
from lumina import auth
from lumina.database.models import MemberModel
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
    responses={
        int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"},
        int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"},
    },
)
def read_member(
    id: str,
    member: MemberModel = Depends(auth.require_member),
):
    if id != member.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot read another member"
        )
    if not member.email_verified:
        lumina.database.operations.set_member_email_verified(member.id)
        # Fetch again, so we get the updated email_verified_at field
        return MemberPrivateResponse.from_model(
            lumina.database.operations.get_member(member.id)
        )
    return MemberPrivateResponse.from_model(member)


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


@router.post(
    "/{id}",
    responses={int(HTTPStatus.CONFLICT): {"description": "Member already exists"}},
)
def register_member(id: str, new_member: RegisterMemberRequest):
    try:
        lumina.database.operations.get_member(id)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Member already exists"
        )
    except lumina.database.operations.ResultNotFound:
        pass

    lumina.database.operations.create_member(
        id=id, name=new_member.full_name, email=new_member.email
    )

    lumina.emails.send.send_email(
        to_addresses=[(new_member.full_name, new_member.email)],
        subject="Finish your registration",
        body=lumina.emails.render.render_email(
            "register_member.html",
            name=new_member.full_name,
            auth_url=auth.get_auth_url(id),
        ),
    )

    return "OK"


@router.put(
    "/{id}",
    responses={
        int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"},
        int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"},
    },
)
def update_member(
    id: str,
    member: MemberModel = Depends(auth.require_member),
):
    if id != member.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot update another member"
        )
    ...


@router.delete(
    "/{id}",
    responses={
        int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"},
        int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"},
    },
)
def delete_member(
    id: str,
    member: MemberModel = Depends(auth.require_member),
):
    if id != member.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot delete another member"
        )
    lumina.database.operations.delete_member(id)
    return "OK"


@router.post(
    "/{id}/login",
    responses={int(HTTPStatus.NOT_FOUND): {"description": "Member not found"}},
)
def send_token_link_for_member(id: str):
    try:
        member = lumina.database.operations.get_member(id)
        lumina.emails.send.send_email(
            to_addresses=[(member.name, member.email)],
            subject="Link to login to Alumni Network",
            body=lumina.emails.render.render_email(
                "login.html",
                name=member.name,
                auth_url=auth.get_auth_url(id),
            ),
        )
    except lumina.database.operations.ResultNotFound:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Member not found")

    return "OK"
