from fastapi import APIRouter, Depends

from lumina import auth
from lumina.schema.auth import AuthCheckResponse

router = APIRouter()


@router.get("/check", response_model=AuthCheckResponse)
def check_auth(
    auth_user: auth.AuthenticatedUser = Depends(auth.require_authenticated_user),
):
    return AuthCheckResponse(id=auth_user.id, expires_at=auth_user.expires_at)
