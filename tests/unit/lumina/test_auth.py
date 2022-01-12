import contextlib
from unittest import mock

import freezegun
import jwt
import pytest
from fastapi.testclient import TestClient
from fixtures import keys

from lumina import auth
from lumina.app import app


@contextlib.contextmanager
def mock_keys():
    with mock.patch(
        "lumina.auth.get_jwt_public_key", return_value=keys.EXAMPLE_PUBLIC_KEY
    ), mock.patch(
        "lumina.auth.get_jwt_private_key", return_value=keys.EXAMPLE_PRIVATE_KEY
    ):
        yield


@mock_keys()
def test_encode_and_decode_token():
    token = auth.encode_jwt("fred_bloggs")
    user = auth.decode_jwt(token)
    assert user.id == "fred_bloggs"


@mock_keys()
def test_invalid_token():
    token = auth.encode_jwt("fred_bloggs")
    with pytest.raises(jwt.InvalidSignatureError):
        auth.decode_jwt(token + "a")


@mock_keys()
def test_expired_token():
    with freezegun.freeze_time("2020-01-01"):
        token = auth.encode_jwt("fred_bloggs")
    with freezegun.freeze_time("2020-03-31"):
        # Valid now
        auth.decode_jwt(token)
    with freezegun.freeze_time("2020-04-01"), pytest.raises(jwt.ExpiredSignatureError):
        # Expired now
        auth.decode_jwt(token)


client = TestClient(app)


class TestRequireAuthenticatedUser:
    @mock_keys()
    def test_returns_user(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-required", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"id": "fred_bloggs"}

    @mock_keys()
    def test_401_on_missing_header(self):
        response = client.get("/test/auth-required")
        assert response.status_code == 401
        assert response.json() == {"detail": "Authorization required"}

    @mock_keys()
    def test_401_on_bad_scheme(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-required", headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Authorization required"}

    @mock_keys()
    def test_401_on_malformed_token(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-required", headers={"Authorization": f"Bearer {token}a"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}

    @mock_keys()
    def test_401_on_expired_token(self):
        with freezegun.freeze_time("2020-01-01"):
            token = auth.encode_jwt("fred_bloggs")
        with freezegun.freeze_time("2020-04-01"):
            response = client.get(
                "/test/auth-required", headers={"Authorization": f"Bearer {token}"}
            )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}


class TestOptionalAuthenticatedUser:
    @mock_keys()
    def test_returns_user(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-optional", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"id": "fred_bloggs"}

    @mock_keys()
    def test_returns_none_on_missing_header(self):
        response = client.get("/test/auth-optional")
        assert response.status_code == 200
        assert response.json() == {"id": None}

    @mock_keys()
    def test_returns_none_on_bad_scheme(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-optional", headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 200
        assert response.json() == {"id": None}

    @mock_keys()
    def test_401_on_malformed_token(self):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            "/test/auth-optional", headers={"Authorization": f"Bearer {token}a"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}

    @mock_keys()
    def test_401_on_expired_token(self):
        with freezegun.freeze_time("2020-01-01"):
            token = auth.encode_jwt("fred_bloggs")
        with freezegun.freeze_time("2020-04-01"):
            response = client.get(
                "/test/auth-optional", headers={"Authorization": f"Bearer {token}"}
            )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}
