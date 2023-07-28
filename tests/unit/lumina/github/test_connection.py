import pytest
from lumina.github import connection


@pytest.mark.vcr
def test_get_content_repo():
    repo = connection.get_content_repo()
    assert repo.name == "lumina-test"
