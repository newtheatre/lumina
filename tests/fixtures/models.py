from unittest.mock import MagicMock

from lumina.database.models import MemberModel

MEMBER_MODEL_FRED_BLOGGS = MemberModel(
    pk="fred_bloggs",
    name="Fred Bloggs",
    email="fred@bloggs.test",
)

GITHUB_ISSUE = MagicMock(
    id=123,
    url="https://github.com/newtheatre/lumina-test/issues/123",
    state="open",
)
