from datetime import datetime, timedelta, timezone
from http import HTTPStatus

import jwt
import lumina.database.operations
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from lumina import ssm
from lumina.database.models import MemberModel
from pydantic import BaseModel

JWT_ALGORITHM = "RS256"
JWT_EXPIRATION_DELTA = timedelta(days=90)
AUTH_URL = "https://nthp-web.pages.dev/auth"


class AuthenticatedToken(BaseModel):
    id: str
    expires_at: datetime


def get_jwt_public_key() -> str:
    """Get public key for JWT verification."""
    return ssm.get_parameter("/lumina/jwt/public")


def get_jwt_private_key() -> str:
    """Get private key for JWT signing."""
    return ssm.get_parameter("/lumina/jwt/private")


def encode_jwt(sub: str) -> str:
    return jwt.encode(
        {
            "sub": sub,
            "exp": datetime.now(tz=timezone.utc) + JWT_EXPIRATION_DELTA,
        },
        get_jwt_private_key(),
        algorithm=JWT_ALGORITHM,
    )


def decode_jwt(token: str) -> AuthenticatedToken:
    payload = jwt.decode(token, get_jwt_public_key(), algorithms=[JWT_ALGORITHM])
    return AuthenticatedToken(id=payload["sub"], expires_at=payload["exp"])


class JWTBearer(HTTPBearer):
    def __init__(self, optional: bool = False):
        self.optional = optional
        super().__init__(auto_error=False)

    async def __call__(self, request: Request) -> AuthenticatedToken | None:  # type: ignore
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            try:
                return decode_jwt(credentials.credentials)
            except jwt.InvalidTokenError as e:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Invalid or expired token",
                ) from e
        elif self.optional:
            return None
        else:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required"
            )


def require_member(
    authenticated_member=Depends(JWTBearer()),  # noqa B008
) -> MemberModel:
    """Get member if token is provided, otherwise raise exception."""
    try:
        return lumina.database.operations.get_member(authenticated_member.id)
    except lumina.database.operations.ResultNotFound as e:
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Member no longer exists",
        ) from e


def optional_member(
    authenticated_member=Depends(JWTBearer(optional=True)),  # noqa B008
) -> MemberModel | None:
    """Get member if token is provided, otherwise return None."""
    if not authenticated_member:
        return None
    return require_member(authenticated_member)


def require_admin(
    member_model: MemberModel = Depends(require_member),
) -> MemberModel:
    """Ensure member is an admin, otherwise raise exception."""
    if not member_model.is_admin:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return member_model


def get_auth_url(sub: str) -> str:
    return f"{AUTH_URL}?token={encode_jwt(sub)}"
