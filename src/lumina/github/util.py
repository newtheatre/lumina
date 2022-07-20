import logging

from lumina.config import settings
from lumina.database.models import GitHubIssueState
from lumina.schema.github import GitHubIssue

log = logging.getLogger(__name__)


def get_content_repo_path(target_type: str, target_id: str) -> str:
    if target_type == "show":
        return f"_shows/{target_id}.md"


def get_content_repo_file_url(path: str, branch: str = "master") -> str:
    return f"https://github.com/{settings.github_owner}/{settings.github_repo}/blob/master/{path}"


def get_content_repo_issue_url(id: int) -> str:
    return (
        f"https://github.com/{settings.github_owner}/{settings.github_repo}/issues/{id}"
    )


def get_state_from_issue(issue: GitHubIssue) -> GitHubIssueState:
    log.info(
        f"Getting state from issue {issue.number}, state={issue.state}, state_reason={issue.state_reason}"
    )
    if issue.state == GitHubIssueState.CLOSED and issue.state_reason == "completed":
        # Catch completed issues as our own 'COMPLETED' state
        return GitHubIssueState.COMPLETED
    return GitHubIssueState(issue.state)
