from pydantic import EmailStr

from lumina.schema.base import LuminaModel


class UserPublicResponse(LuminaModel):
    id: str
    masked_email: str


class UserPrivateResponse(LuminaModel):
    id: str
    email: EmailStr


class RegisterUserRequest(LuminaModel):
    full_name: str
    email: EmailStr
