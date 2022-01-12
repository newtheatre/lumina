from unittest import mock

from fastapi.testclient import TestClient

from lumina.app import app

client = TestClient(app)


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
        assert response.status_code == 200
        assert send_email.called

    def test_invalid_email(self):
        response = client.post(
            "/user/test_id",
            json={
                "email": "test@",
                "fullName": "Test User",
            },
        )
        assert response.status_code == 422
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "email"],
                    "msg": "value is not a valid email address",
                    "type": "value_error.email",
                }
            ]
        }
