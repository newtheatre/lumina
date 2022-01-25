import moto
import pytest

from lumina.database import operations, table
from lumina.database.models import SubmissionModel, SubmitterModel


@pytest.fixture(scope="function", autouse=True)
def create_tables():
    with moto.mock_dynamodb2():
        table.create_tables()
        yield


def test_create_member():
    member = operations.create_member(
        id="fred_bloggs", name="Fred Bloggs", email="fred@bloggs.test"
    )
    assert member.pk == "fred_bloggs"
    assert member.sk == table.SK_PROFILE
    assert member.email == "fred@bloggs.test"
    assert member.phone is None


def test_get_member_exists():
    create_member = operations.create_member(
        id="fred_bloggs", name="Fred Bloggs", email="fred@bloggs.test"
    )
    get_member = operations.get_member(id="fred_bloggs")
    assert create_member == get_member


def test_get_member_doest_exists():
    operations.create_member(
        id="fred_bloggs", name="Fred Bloggs", email="fred@bloggs.test"
    )
    with pytest.raises(operations.ResultNotFound):
        operations.get_member(id="alice_froggs")


def test_put_member():
    create_member = operations.create_member(
        id="fred_bloggs", name="Fred Bloggs", email="fred@bloggs.test"
    )
    create_member.email = "fred.bloggs@gmail.test"
    operations.put_member(create_member)
    get_member = operations.get_member(id="fred_bloggs")
    assert get_member.email == "fred.bloggs@gmail.test"


def test_delete_member_exists():
    create_member = operations.create_member(
        id="fred_bloggs", name="Fred Bloggs", email="fred@bloggs.com"
    )
    operations.delete_member(id=create_member.pk)
    with pytest.raises(operations.ResultNotFound):
        operations.get_member(id=create_member.pk)


def _make_submission(id: int, **kwargs) -> SubmissionModel:
    """Make a SubmissionModel with default values overridable by kwargs."""
    return SubmissionModel(
        **{
            **dict(
                pk="fred_bloggs",
                sk=table.get_submission_sk(id),
                url=f"https://github.com/newtheatre/history-project/issues/{id}",
                target_id="00_01/romeo_and_juliet",
                target_name="Romeo and Juliet",
                target_type="show",
                message="The part of Romeo was played by a hamster.",
                submitter=dict(
                    id="fred_bloggs",
                    name="Fred Bloggs",
                    verified=True,
                ),
            ),
            **kwargs,
        }
    )


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
                email="charlie@bloggs.test",
            ),
        )
    )
    assert create_submission.pk == table.PK_ANONYMOUS


def test_get_submission():
    create_submission = operations.put_submission(_make_submission(101))
    get_submission = operations.get_submission(101)
    assert create_submission == get_submission


def test_get_submissions_for_member():
    sub_1 = operations.put_submission(_make_submission(101, pk="fred_bloggs"))
    sub_2 = operations.put_submission(_make_submission(102, pk="fred_bloggs"))
    operations.put_submission(_make_submission(103, pk="alice_froggs"))
    submissions = operations.get_submissions_for_member("fred_bloggs")
    assert len(submissions) == 2
    assert sub_1 in submissions
    assert sub_2 in submissions


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


def test_get_submission_not_found():
    with pytest.raises(operations.ResultNotFound):
        operations.get_submission(101)
