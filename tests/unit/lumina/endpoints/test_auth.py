from unittest import mock

import freezegun
import pytest
from fastapi.testclient import TestClient
from lumina import auth
from lumina.app import app
from lumina.database.operations import ResultNotFound
from unit.lumina.endpoints.conftest import MEMBER_FRED_BLOGGS

client = TestClient(app)

AUTH_CHECK_REQUIRED_URL = "/auth/check/required"
AUTH_CHECK_OPTIONAL_URL = "/auth/check/optional"


@pytest.fixture(autouse=True)
def mock_get_member():
    with mock.patch(
        "lumina.database.operations.get_member", return_value=MEMBER_FRED_BLOGGS
    ):
        yield


class TestRequireAuthenticatedMember:
    def test_returns_member(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_REQUIRED_URL, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == "fred_bloggs"

    def test_401_on_missing_header(self, mock_keys):
        response = client.get(AUTH_CHECK_REQUIRED_URL)
        assert response.status_code == 401
        assert response.json() == {"detail": "Authorization required"}

    def test_401_on_bad_scheme(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_REQUIRED_URL, headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Authorization required"}

    def test_401_on_malformed_token(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_REQUIRED_URL, headers={"Authorization": f"Bearer {token}a"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}

    def test_401_on_expired_token(self, mock_keys):
        with freezegun.freeze_time("2020-01-01"):
            token = auth.encode_jwt("fred_bloggs")
        with freezegun.freeze_time("2020-04-01"):
            response = client.get(
                AUTH_CHECK_REQUIRED_URL, headers={"Authorization": f"Bearer {token}"}
            )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}

    @mock.patch("lumina.database.operations.get_member", side_effect=ResultNotFound())
    def test_401_on_member_no_longer_exists(self, get_member, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_REQUIRED_URL, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Member no longer exists"}


class TestOptionalAuthenticatedMember:
    def test_returns_member(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_OPTIONAL_URL, headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] == "fred_bloggs"

    def test_returns_none_on_missing_header(self, mock_keys):
        response = client.get(AUTH_CHECK_OPTIONAL_URL)
        assert response.status_code == 200
        assert response.json()["id"] is None

    def test_returns_none_on_bad_scheme(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_OPTIONAL_URL, headers={"Authorization": f"Basic {token}"}
        )
        assert response.status_code == 200
        assert response.json()["id"] is None

    def test_401_on_malformed_token(self, mock_keys):
        token = auth.encode_jwt("fred_bloggs")
        response = client.get(
            AUTH_CHECK_OPTIONAL_URL, headers={"Authorization": f"Bearer {token}a"}
        )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}

    def test_401_on_expired_token(self, mock_keys):
        with freezegun.freeze_time("2020-01-01"):
            token = auth.encode_jwt("fred_bloggs")
        with freezegun.freeze_time("2020-04-01"):
            response = client.get(
                AUTH_CHECK_OPTIONAL_URL, headers={"Authorization": f"Bearer {token}"}
            )
        assert response.status_code == 401
        assert response.json() == {"detail": "Invalid or expired token"}
