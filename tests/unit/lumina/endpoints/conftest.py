import pytest
from lumina.app import app
from lumina.auth import optional_member, require_member
from lumina.database.models import MemberModel

MEMBER_FRED_BLOGGS = MemberModel(
    pk="fred_bloggs",
    name="Fred Bloggs",
    email="fred@bloggs.com",
)


@pytest.fixture()
def auth_fred_bloggs():
    def i_am_fred_bloggs():
        return MEMBER_FRED_BLOGGS

    app.dependency_overrides[require_member] = i_am_fred_bloggs
    app.dependency_overrides[optional_member] = i_am_fred_bloggs

    yield i_am_fred_bloggs()

    del app.dependency_overrides[require_member]
    del app.dependency_overrides[optional_member]
