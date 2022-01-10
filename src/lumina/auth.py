from typing import Optional

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer
from pydantic import BaseModel


class JWTBearer(HTTPBearer):
    def __init__(self, optional: bool = False):
        self.optional = optional
        super(JWTBearer, self).__init__(auto_error=not optional)

    async def __call__(self, request: Request):
        credentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(
                    status_code=403, detail="Invalid authentication scheme."
                )
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(
                    status_code=403, detail="Invalid token or expired token."
                )
            return credentials.credentials
        elif not self.optional:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")

    def verify_jwt(self, token: str) -> bool:
        # TODO: Implement JWT verification
        return True


class AuthenticatedUser(BaseModel):
    id: str


def require_authenticated_user(token=Depends(JWTBearer())) -> AuthenticatedUser:
    """Get user if token is provided, otherwise raise exception."""
    return AuthenticatedUser(id=token)


def optional_authenticated_user(
    token=Depends(JWTBearer(optional=True)),
) -> Optional[AuthenticatedUser]:
    """Get user if token is provided, otherwise return None."""
    if token:
        return AuthenticatedUser(id=token)
    return None
