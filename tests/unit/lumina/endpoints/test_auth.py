from http import HTTPStatus

from unit.lumina.test_auth import client


class TestCheckAuth:
    def test_no_auth(self):
        response = client.get("/auth/check")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_with_auth(self, auth_fred_bloggs):
        response = client.get("/auth/check")
        assert response.status_code == HTTPStatus.OK
        assert response.json()["id"] == auth_fred_bloggs.id
        assert response.json()["expiresAt"] == auth_fred_bloggs.expires_at.isoformat()
