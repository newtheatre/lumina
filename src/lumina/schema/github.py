import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel


class GithubIssueState(Enum):
    OPEN = "open"
    CLOSED = "closed"


class GitHubIssue(BaseModel):
    number: int
    title: str
    state: GithubIssueState
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed_at: Optional[datetime.datetime]


class GitHubRepositoryOwner(BaseModel):
    login: str


class GitHubRepository(BaseModel):
    name: str
    owner: GitHubRepositoryOwner


class GitHubWebhook(BaseModel):
    action: str
    issue: Optional[GitHubIssue]
    repository: GitHubRepository
