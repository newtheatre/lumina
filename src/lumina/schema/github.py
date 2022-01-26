import datetime
from typing import Optional

from pydantic import BaseModel

from lumina.database.models import GitHubIssueState


class GitHubIssue(BaseModel):
    number: int
    state: GitHubIssueState
    title: str
    created_at: datetime.datetime
    updated_at: datetime.datetime
    closed_at: Optional[datetime.datetime]
    comments: int


class GitHubRepositoryOwner(BaseModel):
    login: str


class GitHubRepository(BaseModel):
    name: str
    owner: GitHubRepositoryOwner


class GitHubWebhook(BaseModel):
    action: str
    issue: Optional[GitHubIssue]
    repository: GitHubRepository
