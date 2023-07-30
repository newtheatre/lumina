from http import HTTPStatus

import freezegun
import jwt
import pytest
from fastapi import HTTPException
from lumina import auth
from unit.lumina.endpoints.conftest import MEMBER_ADMIN_BLOGGS, MEMBER_FRED_BLOGGS


def test_encode_and_decode_token(mock_keys):
    token = auth.encode_jwt("fred_bloggs")
    member = auth.decode_jwt(token)
    assert member.id == "fred_bloggs"


def test_invalid_token(mock_keys):
    token = auth.encode_jwt("fred_bloggs")
    with pytest.raises(jwt.InvalidSignatureError):
        auth.decode_jwt(token + "a")


def test_expired_token(mock_keys):
    with freezegun.freeze_time("2020-01-01 00:00"):
        token = auth.encode_jwt("fred_bloggs")
    with freezegun.freeze_time("2020-03-30 23:59"):
        # Valid now
        auth.decode_jwt(token)
    with freezegun.freeze_time("2020-03-31 00:00"), pytest.raises(
        jwt.ExpiredSignatureError
    ):
        # Expired now
        auth.decode_jwt(token)


class TestRequireAdmin:
    def test_success(self):
        member = auth.require_admin(MEMBER_ADMIN_BLOGGS)
        assert member == MEMBER_ADMIN_BLOGGS

    def test_failure(self):
        with pytest.raises(HTTPException) as exc:
            auth.require_admin(MEMBER_FRED_BLOGGS)
        assert exc.value.status_code == HTTPStatus.FORBIDDEN
