from http import HTTPStatus
from unittest import mock

from fastapi.testclient import TestClient
from fixtures.models import GITHUB_ISSUE, MEMBER_MODEL_FRED_BLOGGS

from lumina.app import app
from lumina.database.models import SubmissionModel, SubmitterModel
from lumina.schema.submissions import GenericSubmissionRequest

client = TestClient(app)

DUMMY_SUBMISSION = SubmissionModel(
    pk="fred_bloggs",
    sk="submission/1",
    url="https://github.com/newtheatre/history-project/issues/1",
    target_id="00_01/a_show",
    target_type="show",
    target_name="A Show",
    message="This is a message",
    submitter=SubmitterModel(
        id="fred_bloggs",
        verified=True,
        name="Fred Bloggs",
    ),
)


class TestReadMemberSubmissionStats:
    def test_no_submissions(self):
        with mock.patch(
            "lumina.database.operations.get_submissions_for_member"
        ) as mock_get_submissions:
            mock_get_submissions.return_value = []
            response = client.get("/submissions/member/fred-bloggs/stats")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"count": 0}

    def test_with_submissions(self):
        with mock.patch(
            "lumina.database.operations.get_submissions_for_member"
        ) as mock_get_submissions:
            mock_get_submissions.return_value = [DUMMY_SUBMISSION]
            response = client.get("/submissions/member/fred-bloggs/stats")
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {"count": 1}


class TestCreateGenericSubmission:
    def test_require_submitter_if_not_authed(self):
        response = client.post(
            "/submissions/message",
            json=dict(
                target_type="test",
                target_id="test-page",
                target_name="Test Page",
                target_url="https://example.com/test-page",
                message="Hello World",
            ),
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": "You must either provide a submitter or authenticate as a member"
        }

    def test_require_uuid_submitter_id_if_not_authed(self):
        response = client.post(
            "/submissions/message",
            json=dict(
                target_type="test",
                target_id="test-page",
                target_name="Test Page",
                target_url="https://example.com/test-page",
                message="Hello World",
                submitter=dict(
                    id="fred_bloggs",
                    name="Fred Bloggs",
                    year_of_graduation=2020,
                    email="fred@bloggs.test",
                ),
            ),
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": [
                {
                    "loc": ["body", "submitter", "id"],
                    "msg": "value is not a valid uuid",
                    "type": "type_error.uuid",
                }
            ]
        }

    def test_disallow_submitter_if_authed(self, auth_fred_bloggs):
        response = client.post(
            "/submissions/message",
            json=dict(
                target_type="test",
                target_id="test-page",
                target_name="Test Page",
                target_url="https://example.com/test-page",
                message="Hello World",
                submitter=dict(
                    id="c0286cf1-15cc-4e43-93de-aaca592e447b",
                    name="Fred Bloggs",
                    year_of_graduation=2020,
                    email="fred@bloggs.test",
                ),
            ),
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        assert response.json() == {
            "detail": "You must not provide a submitter if you are authenticated"
        }

    def test_success_not_authed(self):
        with mock.patch(
            "lumina.github.create_generic_submission_issue"
        ) as mock_create_generic_submission_issue, mock.patch(
            "lumina.database.operations.put_submission"
        ) as mock_put_submission:
            submission_request = GenericSubmissionRequest(
                target_type="test",
                target_id="test-page",
                target_name="Test Page",
                target_url="https://example.com/test-page",
                message="Hello World",
                submitter=dict(
                    id="c0286cf1-15cc-4e43-93de-aaca592e447b",
                    name="Fred Bloggs",
                    year_of_graduation=2020,
                    email="fred@bloggs.test",
                ),
            )
            mock_create_generic_submission_issue.return_value = GITHUB_ISSUE
            mock_put_submission.return_value = submission_request.to_model(
                submission_id=123,
                submitter_id=submission_request.submitter.id,
                member=None,
            )
            response = client.post(
                "/submissions/message",
                # This mess needed as pydantic doesn't serialise UUID by default
                # See https://github.com/samuelcolvin/pydantic/issues/1157
                json={
                    **submission_request.dict(),
                    "submitter": {
                        **submission_request.submitter.dict(),
                        "id": str(submission_request.submitter.id),
                    },
                },
            )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "githubIssue": {
                "number": 1,
                "state": "open",
                "url": "https://github.com/newtheatre/lumina-test/issues/123",
            },
            "id": 123,
            "message": "Hello World",
            "submitter": {
                "id": "c0286cf1-15cc-4e43-93de-aaca592e447b",
                "verified": False,
                "name": "Fred Bloggs",
            },
            "targetId": "test-page",
            "targetName": "Test Page",
            "targetType": "test",
            "targetUrl": "https://example.com/test-page",
        }

    def test_success_authed(self, auth_fred_bloggs):
        with mock.patch(
            "lumina.database.operations.get_member"
        ) as mock_get_member, mock.patch(
            "lumina.github.create_generic_submission_issue"
        ) as mock_create_generic_submission_issue, mock.patch(
            "lumina.database.operations.put_submission"
        ) as mock_put_submission:
            submission_request = GenericSubmissionRequest(
                target_type="test",
                target_id="test-page",
                target_name="Test Page",
                target_url="https://example.com/test-page",
                message="Hello World",
            )
            mock_get_member.return_value = MEMBER_MODEL_FRED_BLOGGS
            mock_create_generic_submission_issue.return_value = GITHUB_ISSUE
            mock_put_submission.return_value = submission_request.to_model(
                submission_id=123,
                submitter_id=auth_fred_bloggs.id,
                member=mock_get_member(),
            )
            response = client.post(
                "/submissions/message",
                json=submission_request.dict(),
            )
        assert response.status_code == HTTPStatus.OK
        assert response.json() == {
            "githubIssue": {
                "number": 1,
                "state": "open",
                "url": "https://github.com/newtheatre/lumina-test/issues/123",
            },
            "id": 123,
            "message": "Hello World",
            "submitter": {"id": "fred_bloggs", "verified": True, "name": "Fred Bloggs"},
            "targetId": "test-page",
            "targetName": "Test Page",
            "targetType": "test",
            "targetUrl": "https://example.com/test-page",
        }
