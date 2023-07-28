import datetime

import fixtures.github
from lumina.database.models import GitHubIssueState
from lumina.schema.github import GitHubWebhook


def test_issue_created():
    event = GitHubWebhook(**fixtures.github.WEBHOOK_ISSUE_CREATED)
    assert event.repository.name == "lumina-test"
    assert event.repository.owner.login == "newtheatre"
    assert event.action == "opened"
    assert event.issue.number == 7
    assert event.issue.title == "New Issue"
    assert event.issue.state is GitHubIssueState.OPEN
    assert event.issue.created_at == datetime.datetime(
        2022, 1, 26, 4, 29, 16, tzinfo=datetime.timezone.utc
    )
    assert event.issue.updated_at == datetime.datetime(
        2022, 1, 26, 4, 29, 16, tzinfo=datetime.timezone.utc
    )
    assert event.issue.closed_at is None


def test_issue_comment_created():
    event = GitHubWebhook(**fixtures.github.WEBHOOK_ISSUE_COMMENT_CREATED)
    assert event.repository.name == "lumina-test"
    assert event.repository.owner.login == "newtheatre"
    assert event.action == "created"
    assert event.issue.number == 1
    assert event.issue.title == "Test submission"
    assert event.issue.state is GitHubIssueState.OPEN
    assert event.issue.created_at == datetime.datetime(
        2022, 1, 25, 1, 58, 10, tzinfo=datetime.timezone.utc
    )
    assert event.issue.updated_at == datetime.datetime(
        2022, 1, 26, 4, 16, 36, tzinfo=datetime.timezone.utc
    )
    assert event.issue.closed_at is None


def test_issue_closed():
    event = GitHubWebhook(**fixtures.github.WEBHOOK_ISSUE_CLOSED)
    assert event.repository.name == "lumina-test"
    assert event.repository.owner.login == "newtheatre"
    assert event.action == "closed"
    assert event.issue.number == 1
    assert event.issue.title == "Test submission"
    assert event.issue.state is GitHubIssueState.CLOSED
    assert event.issue.created_at == datetime.datetime(
        2022, 1, 25, 1, 58, 10, tzinfo=datetime.timezone.utc
    )
    assert event.issue.updated_at == datetime.datetime(
        2022, 1, 26, 4, 28, 15, tzinfo=datetime.timezone.utc
    )
    assert event.issue.closed_at == datetime.datetime(
        2022, 1, 26, 4, 28, 15, tzinfo=datetime.timezone.utc
    )


def test_issue_reopened():
    event = GitHubWebhook(**fixtures.github.WEBHOOK_ISSUE_REOPENED)
    assert event.repository.name == "lumina-test"
    assert event.repository.owner.login == "newtheatre"
    assert event.action == "reopened"
    assert event.issue.number == 1
    assert event.issue.title == "Test submission"
    assert event.issue.state is GitHubIssueState.OPEN
    assert event.issue.created_at == datetime.datetime(
        2022, 1, 25, 1, 58, 10, tzinfo=datetime.timezone.utc
    )
    assert event.issue.updated_at == datetime.datetime(
        2022, 1, 26, 4, 28, 46, tzinfo=datetime.timezone.utc
    )
    assert event.issue.closed_at is None
