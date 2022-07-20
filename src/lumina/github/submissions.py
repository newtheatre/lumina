from typing import Optional

from github import Issue

from lumina.database.models import GitHubIssueModel, MemberModel
from lumina.github.connection import get_content_repo
from lumina.github.util import (
    get_content_repo_file_url,
    get_content_repo_path,
    get_state_from_issue,
)
from lumina.schema.submissions import GenericSubmissionRequest, SubmitterRequest


def get_submitter_public_link(id: str) -> str:
    return f"https://history.newtheatre.org.uk/people/{id}"


def get_body_for_submission(
    target_type: str,
    target_id: str,
    message: str,
    submitter: Optional[SubmitterRequest],
    member: Optional[MemberModel],
):
    assert not (submitter and member), "Cannot have both submitter and member"

    repo_file_path = get_content_repo_path(target_type, target_id)
    repo_file_url = get_content_repo_file_url(repo_file_path)

    submitter = (
        f"[{member.name}]({get_submitter_public_link(member.pk)})"
        if member
        else submitter.name
    )

    return f"""
| Name            | Value                                             |
|-----------------|---------------------------------------------------|
| URL             | [/a/b/c](https://history.newtheatre.org.uk/a/b/c) |
| Source          | [{repo_file_path}]({repo_file_url}) |
| Submitter State | {"Member" if member else "Unverified"} |
| Submitter       | {submitter} |

---

{message}"""


def create_generic_submission_issue(
    submission_request: GenericSubmissionRequest, member: Optional[MemberModel]
) -> Issue:
    return get_content_repo().create_issue(
        title=submission_request.subject
        or f"{submission_request.target_type}/{submission_request.target_id}",
        body=get_body_for_submission(
            target_type=submission_request.target_type,
            target_id=submission_request.target_id,
            message=submission_request.message,
            submitter=submission_request.submitter,
            member=member,
        ),
    )


def make_issue_model(issue: Issue) -> GitHubIssueModel:
    return GitHubIssueModel(
        number=issue.number,
        state=issue.state,  # Does not handle completed state but only used for new issues
        title=issue.title,
        created_at=issue.created_at,
        updated_at=issue.updated_at,
        closed_at=issue.closed_at,
        comments=issue.comments,
    )
