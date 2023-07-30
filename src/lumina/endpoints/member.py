from http import HTTPStatus

import lumina.database.operations
import lumina.emails.render
import lumina.emails.send
from fastapi import APIRouter, Depends, HTTPException
from lumina import auth
from lumina.database.models import MemberModel
from lumina.schema.member import (
    MemberPrivateResponse,
    MemberPublicResponse,
    RegisterMemberRequest,
    UpdateMemberRequest,
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
    member_model: MemberModel = Depends(auth.require_member),
):
    """
    Read a member's details.
    Requires permission to view, only works for your own profile.
    """
    if id != member_model.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot read another member"
        )
    if not member_model.email_verified:
        lumina.database.operations.set_member_email_verified(member_model.id)
        # Fetch again, so we get the updated email_verified_at field
        return MemberPrivateResponse.from_model(
            lumina.database.operations.get_member(member_model.id)
        )
    if member_model.anonymous_ids:
        for anonymous_id in member_model.anonymous_ids:
            lumina.database.operations.move_anonymous_submissions_to_member(
                member_id=member_model.id,
                anonymous_id=anonymous_id,
            )
    return MemberPrivateResponse.from_model(member_model)


@router.get(
    "/{id}/check",
    response_model=MemberPublicResponse,
    responses={int(HTTPStatus.NOT_FOUND): {"description": "Member not found"}},
)
def check_member(id: str):
    """Check if a member exists for an ID. Use to check if a member has registered."""
    try:
        member = lumina.database.operations.get_member(id)
        return MemberPublicResponse(id=member.pk, masked_email=mask_email(member.email))
    except lumina.database.operations.ResultNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Member not found"
        ) from e


@router.post(
    "/{id}",
    responses={int(HTTPStatus.CONFLICT): {"description": "Member already exists"}},
)
def register_member(id: str, new_member: RegisterMemberRequest):
    """
    Register a new member.
    After success the member will be emailed a link to complete registration.
    """
    try:
        lumina.database.operations.get_member(id)
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="Member already exists"
        )
    except lumina.database.operations.ResultNotFound:
        pass

    lumina.database.operations.put_member(new_member.to_model(id))

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
    member_update: UpdateMemberRequest,
    member_model: MemberModel = Depends(auth.require_member),
) -> MemberPrivateResponse:
    """
    Update certain fields of a member.
    Requires permission to update, only works for your own profile.
    """
    if id != member_model.id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="You cannot update another member"
        )
    try:
        existing_member = lumina.database.operations.get_member(id)
    except lumina.database.operations.ResultNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Member not found"
        ) from e

    existing_member.phone = member_update.phone
    existing_member.consent = member_update.consent.to_model()

    updated_member = lumina.database.operations.put_member(existing_member)
    return MemberPrivateResponse.from_model(updated_member)


@router.delete(
    "/{id}",
    responses={
        int(HTTPStatus.UNAUTHORIZED): {"description": "Unauthorized"},
        int(HTTPStatus.FORBIDDEN): {"description": "Forbidden"},
    },
)
def delete_member(
    id: str,
    member_model: MemberModel = Depends(auth.require_member),
):
    """
    Delete a member.
    Requires permission to delete, only works for your own profile.
    """
    if id != member_model.id:
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
    """
    Send a link to log in to the registered email address of a member.
    """
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
    except lumina.database.operations.ResultNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="Member not found"
        ) from e

    return "OK"
