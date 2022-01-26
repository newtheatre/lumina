from unittest.mock import MagicMock

from lumina.database.models import MemberModel

MEMBER_MODEL_FRED_BLOGGS = MemberModel(
    pk="fred_bloggs",
    name="Fred Bloggs",
    email="fred@bloggs.test",
)

GITHUB_ISSUE = MagicMock(
    number=123,
    html_url="https://github.com/newtheatre/lumina-test/issues/123",
    state="open",
    title="Test issue",
    created_at="2020-01-01T00:00:00Z",
    updated_at="2020-01-01T00:00:00Z",
    closed_at=None,
    comments=0,
)
