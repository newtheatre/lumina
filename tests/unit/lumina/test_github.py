from os import environ
from unittest import mock

import pytest

from lumina import github
from lumina.database.models import MemberModel
from lumina.schema.submissions import GenericSubmissionRequest, SubmitterRequest


@pytest.fixture(autouse=True)
def mock_token():
    # To generate VCR cassettes, set the environment variable `GITHUB_TOKEN` to the
    # test access token. This way we can generate test cassettes against the real
    # GitHub API without committing secrets.
    with mock.patch(
        "lumina.github.get_access_token", return_value=environ.get("GITHUB_TOKEN")
    ):
        yield


@pytest.mark.vcr
def test_get_content_repo():
    repo = github.get_content_repo()
    assert repo.name == "lumina-test"


@pytest.mark.vcr
def test_create_generic_submission_issue_anonymous():
    issue = github.create_generic_submission_issue(
        submission_request=GenericSubmissionRequest(
            target_type="show",
            target_id="11_12/faust_is_dead",
            target_name="Faust is Dead",
            target_url="https://history.newtheatre.org.uk/years/11_12/faust_is_dead/",
            subject="Test submission",
            message="This is a test submission.",
            submitter=SubmitterRequest(
                id="c0286cf1-15cc-4e43-93de-aaca592e447b",
                name="Fred Bloggs",
                email="fred@bloggs.com",
                year_of_graduation=2020,
            ),
        ),
        member=None,
    )
    assert issue.title == "Test submission"
    assert issue.number == 1


@pytest.mark.vcr
def test_create_generic_submission_issue_anonymous_no_subject():
    issue = github.create_generic_submission_issue(
        submission_request=GenericSubmissionRequest(
            target_type="show",
            target_id="11_12/faust_is_dead",
            target_name="Faust is Dead",
            target_url="https://history.newtheatre.org.uk/years/11_12/faust_is_dead/",
            subject=None,
            message="This is a test submission.",
            submitter=SubmitterRequest(
                id="c0286cf1-15cc-4e43-93de-aaca592e447b",
                name="Fred Bloggs",
                email="fred@bloggs.com",
                year_of_graduation=2020,
            ),
        ),
        member=None,
    )
    assert issue.title == "show/11_12/faust_is_dead"
    assert issue.number == 2
    assert issue.state == "open"


@pytest.mark.vcr
def test_create_generic_submission_issue_member():
    issue = github.create_generic_submission_issue(
        submission_request=GenericSubmissionRequest(
            target_type="show",
            target_id="11_12/faust_is_dead",
            target_name="Faust is Dead",
            target_url="https://history.newtheatre.org.uk/years/11_12/faust_is_dead/",
            subject="Test submission",
            message="This is a test submission.",
            submitter=None,
        ),
        member=MemberModel(
            pk="fred_bloggs",
            name="Fred Bloggs",
            email="fred@bloggs.com",
            year_of_graduation=2020,
        ),
    )
    assert issue.title == "Test submission"
    assert issue.number == 3
    assert issue.state == "open"
