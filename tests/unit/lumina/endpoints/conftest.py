from contextlib import contextmanager

import pytest
from lumina.app import app
from lumina.auth import optional_member, require_member
from lumina.database.models import MemberModel


@contextmanager
def mock_auth_member(member: MemberModel):
    def i_am_member():
        return member

    app.dependency_overrides[require_member] = i_am_member
    app.dependency_overrides[optional_member] = i_am_member

    yield i_am_member()

    del app.dependency_overrides[require_member]
    del app.dependency_overrides[optional_member]


MEMBER_FRED_BLOGGS = MemberModel(
    pk="fred_bloggs",
    name="Fred Bloggs",
    email="fred@bloggs.com",
)
MEMBER_ADMIN_BLOGGS = MemberModel(
    pk="admin_bloggs",
    name="Admin Bloggs",
    email="admin@bloggs.com",
    is_admin=True,
)


@pytest.fixture()
def auth_fred_bloggs():
    with mock_auth_member(MEMBER_FRED_BLOGGS):
        yield MEMBER_FRED_BLOGGS


@pytest.fixture()
def auth_admin_bloggs():
    with mock_auth_member(MEMBER_ADMIN_BLOGGS):
        yield MEMBER_ADMIN_BLOGGS
