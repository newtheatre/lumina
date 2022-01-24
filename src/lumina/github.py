import functools
from typing import Optional

from github import Github, Issue, Repository

from lumina import ssm
from lumina.config import settings
from lumina.database.models import MemberModel
from lumina.schema.submissions import GenericSubmissionRequest, SubmitterRequest


def get_access_token() -> str:
    return ssm.get_parameter("/lumina/github/access-token")


@functools.lru_cache(maxsize=1)
def get_content_repo() -> Repository:
    client = Github(get_access_token())
    return client.get_repo(f"{settings.github_owner}/{settings.github_repo}")


def get_content_repo_path(target_type: str, target_id: str) -> str:
    if target_type == "show":
        return f"_shows/{target_id}.md"


def get_content_repo_file_url(path: str, branch: str = "master") -> str:
    return f"https://github.com/newtheatre/history-project/blob/master/{path}"


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
