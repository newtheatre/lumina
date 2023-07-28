import datetime

from lumina.database.models import GitHubIssueState
from pydantic import BaseModel


class GitHubIssue(BaseModel):
    number: int
    state: GitHubIssueState
    state_reason: str | None
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed_at: datetime.datetime | None
    comments: int


class GitHubRepositoryOwner(BaseModel):
    login: str


class GitHubRepository(BaseModel):
    name: str
    owner: GitHubRepositoryOwner


class GitHubWebhook(BaseModel):
    action: str
    issue: GitHubIssue | None
    repository: GitHubRepository
