import functools

from github import Github
from github.Repository import Repository

from lumina import ssm
from lumina.config import settings


def get_access_token() -> str:
    return ssm.get_parameter("/lumina/github/access-token")


@functools.lru_cache(maxsize=1)
def get_content_repo() -> Repository:
    client = Github(get_access_token())
    return client.get_repo(f"{settings.github_owner}/{settings.github_repo}")
