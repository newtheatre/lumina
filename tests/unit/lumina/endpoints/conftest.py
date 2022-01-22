import datetime

import pytest

from lumina.app import app
from lumina.auth import (
    AuthenticatedMember,
    optional_authenticated_member,
    require_authenticated_member,
)


@pytest.fixture()
def auth_fred_bloggs():
    def i_am_fred_bloggs():
        return AuthenticatedMember(
            id="fred_bloggs",
            expires_at=datetime.datetime.utcnow() + datetime.timedelta(days=1),
        )

    app.dependency_overrides[require_authenticated_member] = i_am_fred_bloggs
    app.dependency_overrides[optional_authenticated_member] = i_am_fred_bloggs
    yield i_am_fred_bloggs()
    del app.dependency_overrides[require_authenticated_member]
    del app.dependency_overrides[optional_authenticated_member]
