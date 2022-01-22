from fastapi import APIRouter, Depends

from lumina import auth
from lumina.schema.auth import AuthCheckResponse

router = APIRouter()


@router.get("/check", response_model=AuthCheckResponse)
def check_auth(
    member: auth.AuthenticatedMember = Depends(auth.require_authenticated_member),
):
    return AuthCheckResponse(id=member.id, expires_at=member.expires_at)
