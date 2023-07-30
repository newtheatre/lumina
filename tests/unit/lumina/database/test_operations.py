import datetime
import uuid

import freezegun
import moto
import pytest
from lumina.database import operations, table
from lumina.database.models import (
    GitHubIssueModel,
    GitHubIssueState,
    MemberModel,
    SubmissionModel,
    SubmitterModel,
)
from lumina.util import dates


@pytest.fixture(scope="function", autouse=True)
def create_tables():
    with moto.mock_dynamodb():
        table.create_tables()
        yield


@pytest.fixture()
def fred_bloggs() -> MemberModel:
    return operations.create_member(
        MemberModel(
            pk="fred_bloggs",
            name="Fred Bloggs",
            email="fred@bloggs.com",
            anonymous_id=uuid.uuid4(),
        )
    )


def test_create_member(fred_bloggs):
    assert fred_bloggs.pk == "fred_bloggs"
    assert fred_bloggs.sk == table.SK_PROFILE
    assert fred_bloggs.email == "fred@bloggs.com"
    assert fred_bloggs.phone is None


def test_get_member_exists(fred_bloggs):
    assert fred_bloggs == operations.get_member(id="fred_bloggs")


def test_get_member_doest_exists(fred_bloggs):
    with pytest.raises(operations.ResultNotFound):
        operations.get_member(id="alice_froggs")


def test_put_member(fred_bloggs):
    fred_bloggs.email = "fred.bloggs@bloggs.com"
    operations.put_member(fred_bloggs)
    get_member = operations.get_member(id="fred_bloggs")
    assert get_member.email == "fred.bloggs@bloggs.com"


def test_set_member_email_verified(fred_bloggs):
    assert fred_bloggs.email_verified is False
    with freezegun.freeze_time("2020-01-01 12:34:56"):
        operations.set_member_email_verified(fred_bloggs.pk)
    get_member = operations.get_member(fred_bloggs.pk)
    assert get_member.email_verified is True
    assert get_member.email_verified_at == datetime.datetime(
        2020, 1, 1, 12, 34, 56, tzinfo=datetime.timezone.utc
    )


def test_delete_member_exists(fred_bloggs):
    operations.delete_member(id=fred_bloggs.pk)
    with pytest.raises(operations.ResultNotFound):
        operations.get_member(id=fred_bloggs.pk)


def _make_submission(id: int, **kwargs) -> SubmissionModel:
    """Make a SubmissionModel with default values overridable by kwargs."""
    return SubmissionModel(
        pk="fred_bloggs",
        sk=table.get_submission_sk(id),
        url=f"https://github.com/newtheatre/history-project/issues/{id}",
        target_id="00_01/romeo_and_juliet",
        target_name="Romeo and Juliet",
        target_type="show",
        message="The part of Romeo was played by a hamster.",
        created_at=dates.now(),
        submitter=SubmitterModel(
            id="fred_bloggs",
            name="Fred Bloggs",
            verified=True,
        ),
        github_issue=GitHubIssueModel(
            number=id,
            state="open",
            title="Romeo and Juliet",
            created_at=dates.now(),
            updated_at=dates.now(),
            closed_at=None,
            comments=0,
        ),
    ).copy(update=kwargs)


def test_put_member_submission():
    create_submission = operations.put_submission(_make_submission(101))
    assert create_submission.pk == "fred_bloggs"
    assert create_submission.sk == "submission/101"


def test_put_anonymous_submission():
    create_submission = operations.put_submission(
        _make_submission(
            101,
            pk=table.PK_ANONYMOUS,
            submitter=SubmitterModel(
                id="c0286cf1-15cc-4e43-93de-aaca592e447b",
                verified=False,
                name="Charlie Bloggs",
                email="charlie@bloggs.com",
            ),
        )
    )
    assert create_submission.pk == table.PK_ANONYMOUS


def test_get_submission(fred_bloggs):
    create_submission = operations.put_submission(_make_submission(101))
    get_submission = operations.get_submission(101)
    assert create_submission == get_submission


def test_get_submission_not_found():
    with pytest.raises(operations.ResultNotFound):
        operations.get_submission(101)


def test_get_submissions_for_member(fred_bloggs):
    sub_1 = operations.put_submission(_make_submission(101, pk=fred_bloggs.pk))
    sub_2 = operations.put_submission(_make_submission(102, pk=fred_bloggs.pk))
    operations.put_submission(_make_submission(103, pk="alice_froggs"))
    submissions = operations.get_submissions_for_member(fred_bloggs.pk)
    assert len(submissions) == 2
    assert sub_1 in submissions
    assert sub_2 in submissions


def test_get_submissions_for_member_no_submissions(fred_bloggs):
    submissions = operations.get_submissions_for_member(fred_bloggs.pk)
    assert len(submissions) == 0


def test_get_submissions_for_target():
    show_submission_1 = operations.put_submission(
        _make_submission(99, target_type="show", target_id="00_01/romeo_and_juliet")
    )
    show_submission_2 = operations.put_submission(
        _make_submission(101, target_type="show", target_id="00_01/romeo_and_juliet")
    )
    operations.put_submission(
        _make_submission(102, target_type="show", target_id="02_03/east")
    )
    operations.put_submission(
        _make_submission(103, target_type="person", target_id="fred_bloggs")
    )
    submissions = operations.get_submissions_for_target(
        target_type="show", target_id="00_01/romeo_and_juliet"
    )
    assert len(submissions) == 2
    assert show_submission_1 in submissions
    assert show_submission_2 in submissions


def test_update_submission_github_issue():
    new_submission = operations.put_submission(_make_submission(101))
    assert new_submission.github_issue.state == GitHubIssueState.OPEN
    assert new_submission.github_issue.closed_at is None
    assert new_submission.github_issue.comments == 0
    to_close_at = dates.now()
    operations.update_submission_github_issue(
        101,
        new_submission.github_issue.copy(
            update={
                "state": GitHubIssueState.CLOSED,
                "comments": 5,
                "closed_at": to_close_at,
            }
        ),
    )
    updated_submission = operations.get_submission(101)
    assert updated_submission.github_issue.state == GitHubIssueState.CLOSED
    assert updated_submission.github_issue.closed_at == to_close_at
    assert updated_submission.github_issue.comments == 5


def test_move_anonymous_submissions_to_member(fred_bloggs):
    anonymous_id = uuid.uuid4()
    operations.put_submission(
        _make_submission(
            99, pk=anonymous_id, target_type="show", target_id="00_01/romeo_and_juliet"
        )
    )
    operations.put_submission(
        _make_submission(
            101, pk=anonymous_id, target_type="show", target_id="00_01/romeo_and_juliet"
        )
    )
    operations.put_submission(
        _make_submission(
            102, pk="alice_froggs", target_type="show", target_id="02_03/east"
        )
    )

    # There should be no submissions for fred_bloggs
    assert len(operations.get_submissions_for_member(fred_bloggs.pk)) == 0
    # There should be two anonymous submissions
    assert len(operations.get_submissions_for_member(anonymous_id)) == 2
    # Move these submissions to fred_bloggs
    submissions = operations.move_anonymous_submissions_to_member(
        member_id=fred_bloggs.pk, anonymous_id=anonymous_id
    )
    # Two submission returned
    assert len(submissions) == 2
    # There should be two submissions for fred_bloggs
    assert len(operations.get_submissions_for_member(fred_bloggs.pk)) == 2
    # There should be no anonymous submissions
    assert len(operations.get_submissions_for_member(anonymous_id)) == 0
