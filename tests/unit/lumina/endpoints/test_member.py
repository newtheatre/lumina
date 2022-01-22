from http import HTTPStatus
from unittest import mock

from fastapi.testclient import TestClient

from lumina.app import app
from lumina.database.models import MemberModel
from lumina.database.operations import ResultNotFound

client = TestClient(app)

MEMBER_MODEL_FRED_BLOGGS = MemberModel(
    pk="fred_bloggs",
    name="Fred Bloggs",
    email="fred@bloggs.test",
)


class TestCheckMember:
    @mock.patch(
        "lumina.database.operations.get_member",
        return_value=MEMBER_MODEL_FRED_BLOGGS,
    )
    def test_check_member_found(self, mock_get_member):
        response = client.get("/member/fred_bloggs/check")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "id": "fred_bloggs",
            "maskedEmail": "fr***@bl***.test",
        }

    @mock.patch("lumina.database.operations.get_member", side_effect=ResultNotFound())
    def test_check_member_not_found(self, mock_get_member):
        response = client.get("/member/fred_bloggs/check")
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestRegisterMember:
    @mock.patch("lumina.database.operations.create_member", return_value=None)
    @mock.patch("lumina.database.operations.get_member", side_effect=ResultNotFound())
    @mock.patch(
        "lumina.auth.get_auth_url", return_value="https://nthp.test/auth?token=123"
    )
    @mock.patch("lumina.emails.send.send_email", return_value="abc123")
    def test_success(self, send_email, get_auth_url, get_member, create_member):
        response = client.post(
            "/member/fred_bloggs",
            json={
                "email": "test@example.com",
                "fullName": "Fred Bloggs",
            },
        )
        assert response.status_code == HTTPStatus.OK
        assert get_member.called
        assert send_email.called

    @mock.patch(
        "lumina.database.operations.get_member",
        return_value=MEMBER_MODEL_FRED_BLOGGS,
    )
    @mock.patch(
        "lumina.auth.get_auth_url", return_value="https://nthp.test/auth?token=123"
    )
    @mock.patch("lumina.emails.send.send_email", return_value="abc123")
    def test_conflict_member_already_exists(self, send_email, get_auth_url, get_member):
        response = client.post(
            "/member/test_id",
            json={
                "email": "test@example.com",
                "fullName": "Fred Bloggs",
            },
        )
        assert response.status_code == HTTPStatus.CONFLICT
        assert get_member.called
        assert not send_email.called

    def test_invalid_email(self):
        response = client.post(
            "/member/test_id",
            json={
                "email": "test@",
                "fullName": "Test Member",
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


class TestDeleteMember:
    def test_no_auth(self):
        response = client.delete("/member/fred_bloggs")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_cannot_delete_others(self, auth_fred_bloggs):
        response = client.delete("/member/alice_bloggs")
        assert response.status_code == HTTPStatus.FORBIDDEN
        assert response.json() == {"detail": "You cannot delete another member"}

    @mock.patch("lumina.database.operations.delete_member", return_value=None)
    def test_success(self, mock_delete_member, auth_fred_bloggs):
        response = client.delete("/member/fred_bloggs")
        assert response.status_code == HTTPStatus.OK
        assert mock_delete_member.called
