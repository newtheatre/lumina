from unittest import mock

import fixtures.github
import pytest
from lumina.database.models import GitHubIssueModel, GitHubIssueState
from lumina.database.operations import ResultNotFound
from lumina.github import webhooks
from lumina.schema.github import (
    GitHubIssue,
    GitHubRepository,
    GitHubRepositoryOwner,
    GitHubWebhook,
)


@pytest.fixture(autouse=True)
def mock_webhook_secret():
    with mock.patch(
        "lumina.github.webhooks.get_webhook_secret",
        return_value=fixtures.github.SIGNED_SECRET,
    ):
        yield


class TestVerifyWebhook:
    def test_valid(self):
        assert (
            webhooks.verify_webhook(
                signature=fixtures.github.SIGNED_HEADER,
                body=fixtures.github.SIGNED_BODY.encode(),
            )
            is True
        )

    def test_invalid(self):
        assert (
            webhooks.verify_webhook(
                signature=fixtures.github.SIGNED_HEADER,
                body=(fixtures.github.SIGNED_BODY + "a").encode(),
            )
            is False
        )


ISSUE_CLOSED_HOOK = GitHubWebhook(
    action="closed",
    issue=GitHubIssue(
        number=1,
        state=GitHubIssueState.CLOSED,
        title="Issue 1",
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        closed_at="2020-01-02T00:00:00Z",
        comments=2,
    ),
    repository=GitHubRepository(
        name="lumina-test",
        owner=GitHubRepositoryOwner(login="newtheatre"),
    ),
)

ISSUE_COMPLETED_HOOK = GitHubWebhook(
    action="closed",
    issue=GitHubIssue(
        number=1,
        state=GitHubIssueState.CLOSED,
        title="Issue 1",
        created_at="2020-01-01T00:00:00Z",
        updated_at="2020-01-01T00:00:00Z",
        closed_at="2020-01-02T00:00:00Z",
        comments=2,
        state_reason="completed",
    ),
    repository=GitHubRepository(
        name="lumina-test",
        owner=GitHubRepositoryOwner(login="newtheatre"),
    ),
)


class TestHandleWebhook:
    def test_issue_closed(self):
        with mock.patch(
            "lumina.database.operations.update_submission_github_issue",
            return_value=None,
        ) as mock_update_issue:
            webhooks.handle_webhook(ISSUE_CLOSED_HOOK)
        assert mock_update_issue.call_count == 1
        assert mock_update_issue.call_args[0][1] == GitHubIssueModel(
            **ISSUE_CLOSED_HOOK.issue.dict()
        )

    def test_issue_completed(self):
        with mock.patch(
            "lumina.database.operations.update_submission_github_issue",
            return_value=None,
        ) as mock_update_issue:
            webhooks.handle_webhook(ISSUE_COMPLETED_HOOK)
        assert mock_update_issue.call_count == 1
        saved_issue: GitHubIssueModel = mock_update_issue.call_args[0][1]
        assert saved_issue.state == GitHubIssueState.COMPLETED

    def test_issue_doesnt_exist(self):
        with mock.patch(
            "lumina.database.operations.update_submission_github_issue",
            side_effect=ResultNotFound,
        ):
            webhooks.handle_webhook(ISSUE_CLOSED_HOOK)
