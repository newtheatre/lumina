from uuid import UUID

from boto3.dynamodb.conditions import Key
from lumina.database.models import GitHubIssueModel, MemberModel
from lumina.util import dates

from .models import SubmissionModel
from .table import (
    GSI_SK,
    GSI_SUBMISSION_TARGET,
    GSI_SUBMISSION_TARGET_PK,
    GSI_SUBMISSION_TARGET_SK,
    MEMBER_PARTITION_KEY,
    MEMBER_SORT_KEY,
    SK_PROFILE,
    SK_SUBMISSION_PREFIX,
    get_member_table,
    get_submission_sk,
)


class DbError(Exception):
    pass


class ResultNotFound(DbError):
    pass


def get_members() -> list[MemberModel]:
    options = {
        "IndexName": GSI_SK,
        "KeyConditionExpression": Key(MEMBER_SORT_KEY).eq(SK_PROFILE),
    }
    response = get_member_table().query(**options) # type: ignore
    data = response["Items"]
    while response.get("LastEvaluatedKey"):
        response = get_member_table().scan(
            ExclusiveStartKey=response["LastEvaluatedKey"],
            **options, # type: ignore
        )
        data.extend(response["Items"])
    return [MemberModel(**item) for item in data]


def get_member(id: str) -> MemberModel:
    response = get_member_table().get_item(
        Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE}
    )
    if result := response.get("Item"):
        return MemberModel(**result)
    raise ResultNotFound(f"Member with id {id} not found")


def put_member(model: MemberModel) -> MemberModel:
    get_member_table().put_item(Item=model.ddict())
    return model


def set_member_email_verified(id: str) -> None:
    get_member_table().update_item(
        Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE},
        UpdateExpression="set email_verified_at = :v",
        ExpressionAttributeValues={":v": dates.now().isoformat()},
    )


def delete_member(id: str) -> None:
    get_member_table().delete_item(
        Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE}
    )


def get_submission(id: int) -> SubmissionModel:
    response = get_member_table().query(
        IndexName=GSI_SK,
        KeyConditionExpression=Key(MEMBER_SORT_KEY).eq(get_submission_sk(id)),
    )
    if response["Count"] == 0:
        raise ResultNotFound(f"Submission with id {id} not found")
    if response["Count"] > 1:
        raise DbError(f"Multiple submissions with id {id} found")
    return SubmissionModel(**response["Items"][0])  # type: ignore


def get_submissions_for_member(id: str | UUID) -> list[SubmissionModel]:
    response = get_member_table().query(
        KeyConditionExpression=Key(MEMBER_PARTITION_KEY).eq(str(id))
        & Key(MEMBER_SORT_KEY).begins_with(SK_SUBMISSION_PREFIX),
    )
    return [SubmissionModel(**item) for item in response["Items"]]  # type: ignore


def get_submissions_for_target(
    target_type: str, target_id: str
) -> list[SubmissionModel]:
    response = get_member_table().query(
        IndexName=GSI_SUBMISSION_TARGET,
        KeyConditionExpression=Key(GSI_SUBMISSION_TARGET_PK).eq(target_type)
        & Key(GSI_SUBMISSION_TARGET_SK).eq(target_id),
    )
    return [SubmissionModel(**item) for item in response["Items"]]  # type: ignore


def put_submission(model: SubmissionModel) -> SubmissionModel:
    get_member_table().put_item(Item=model.ddict())
    return model


def update_submission_github_issue(id: int, issue: GitHubIssueModel) -> SubmissionModel:
    submission = get_submission(id)
    get_member_table().update_item(
        Key={
            MEMBER_PARTITION_KEY: submission.pk,
            MEMBER_SORT_KEY: get_submission_sk(id),
        },
        UpdateExpression="set github_issue = :v",
        ExpressionAttributeValues={":v": issue.ddict()},
    )
    return get_submission(id)


def move_anonymous_submissions_to_member(
    member_id: str, anonymous_id: UUID
) -> list[SubmissionModel]:
    """Delete all submissions for the anonymous member and create them as member
    submissions."""
    anonymous_submissions = get_submissions_for_member(anonymous_id)
    new_member_submissions = []
    for anonymous_submission in anonymous_submissions:
        # Create a new submission using the member ID
        new_member_submissions.append(
            # Direct copy and change only the PK
            put_submission(anonymous_submission.model_copy(update={"pk": member_id}))
        )
        # Delete the old submission
        delete_response = get_member_table().delete_item(
            Key={
                MEMBER_PARTITION_KEY: anonymous_submission.pk,
                MEMBER_SORT_KEY: anonymous_submission.sk,
            },
            ReturnValues="ALL_OLD",  # Needed for 'Attributes' in response
        )
        assert delete_response["Attributes"], "Original submission not deleted"
    return new_member_submissions
