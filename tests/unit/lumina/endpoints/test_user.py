from http import HTTPStatus
from unittest import mock

from fastapi.testclient import TestClient

from lumina.app import app
from lumina.database.models import MemberModel
from lumina.database.operations import ResultNotFound

client = TestClient(app)


class TestCheckUser:
    @mock.patch(
        "lumina.database.operations.get_member",
        return_value=MemberModel(
            pk="fred_bloggs",
            name="Fred Bloggs",
            email="fred@bloggs.test",
        ),
    )
    def test_check_member_found(self, mock_get_member):
        response = client.get("/user/fred_bloggs/check")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "id": "fred_bloggs",
            "maskedEmail": "fr***@bl***.test",
        }

    @mock.patch("lumina.database.operations.get_member", side_effect=ResultNotFound())
    def test_check_member_not_found(self, mock_get_member):
        response = client.get("/user/fred_bloggs/check")
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestRegisterUser:
    @mock.patch("lumina.emails.send.send_email", return_value="abc123")
    @mock.patch(
        "lumina.auth.get_auth_url", return_value="https://nthp.test/auth?token=123"
    )
    def test_success(self, send_email, get_auth_url):
        response = client.post(
            "/user/test_id",
            json={
                "email": "test@example.com",
                "fullName": "Test User",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert send_email.called

    def test_invalid_email(self):
        response = client.post(
            "/user/test_id",
            json={
                "email": "test@",
                "fullName": "Test User",
            },
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ]
        }
