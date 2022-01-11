from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from typing import Optional

import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from lumina import ssm

JWT_ALGORITHM = "RS256"
JWT_EXPIRATION_DELTA = timedelta(days=90)


class AuthenticatedUser(BaseModel):
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


def decode_jwt(token: str) -> AuthenticatedUser:
    payload = jwt.decode(token, get_jwt_public_key(), algorithms=[JWT_ALGORITHM])
    return AuthenticatedUser(id=payload["sub"], expires_at=payload["exp"])


class JWTBearer(HTTPBearer):
    def __init__(self, optional: bool = False):
        self.optional = optional
        super(JWTBearer, self).__init__(auto_error=False)

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            try:
                return decode_jwt(credentials.credentials)
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    detail="Invalid or expired token",
                )
        elif self.optional:
            return None
        else:
            raise HTTPException(
                status_code=HTTPStatus.UNAUTHORIZED, detail="Authorization required"
            )


def require_authenticated_user(
    authenticated_user=Depends(JWTBearer()),
) -> AuthenticatedUser:
    """Get user if token is provided, otherwise raise exception."""
    return authenticated_user


def optional_authenticated_user(
    authenticated_user=Depends(JWTBearer(optional=True)),
) -> Optional[AuthenticatedUser]:
    """Get user if token is provided, otherwise return None."""
    return authenticated_user
