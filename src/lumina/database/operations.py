from typing import List

from boto3.dynamodb.conditions import Key

from lumina.database.models import GitHubIssueModel, MemberModel
from lumina.util import dates

from .connection import get_dynamo_db
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
    get_submission_sk,
    get_table_name,
)


class DbError(Exception):
    pass


class ResultNotFound(DbError):
    pass


def create_member(id: str, name: str, email: str) -> MemberModel:
    member_model = MemberModel(pk=id, name=name, email=email)
    get_dynamo_db().Table(get_table_name()).put_item(
        Item=member_model.ddict(),
    )

    return member_model


def get_member(id: str) -> MemberModel:
    response = (
        get_dynamo_db()
        .Table(get_table_name())
        .get_item(Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE})
    )
    if result := response.get("Item"):
        return MemberModel(**result)
    raise ResultNotFound(f"Member with id {id} not found")


def put_member(model: MemberModel) -> MemberModel:
    get_dynamo_db().Table(get_table_name()).put_item(
        Item=model.ddict(),
    )
    return model


def set_member_email_verified(id: str) -> None:
    get_dynamo_db().Table(get_table_name()).update_item(
        Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE},
        UpdateExpression="set email_verified_at = :v",
        ExpressionAttributeValues={":v": dates.now().isoformat()},
    )


def delete_member(id: str) -> None:
    get_dynamo_db().Table(get_table_name()).delete_item(
        Key={MEMBER_PARTITION_KEY: id, MEMBER_SORT_KEY: SK_PROFILE}
    )


def get_submission(id: int) -> SubmissionModel:
    response = (
        get_dynamo_db()
        .Table(get_table_name())
        .query(
            IndexName=GSI_SK,
            KeyConditionExpression=Key(GSI_SK).eq(get_submission_sk(id)),
        )
    )
    if response["Count"] == 0:
        raise ResultNotFound(f"Submission with id {id} not found")
    if response["Count"] > 1:
        raise DbError(f"Multiple submissions with id {id} found")
    return SubmissionModel(**response["Items"][0])


def get_submissions_for_member(id: str) -> List[SubmissionModel]:
    response = (
        get_dynamo_db()
        .Table(get_table_name())
        .query(
            KeyConditionExpression=Key(MEMBER_PARTITION_KEY).eq(id)
            & Key(MEMBER_SORT_KEY).begins_with(SK_SUBMISSION_PREFIX),
        )
    )
    return [SubmissionModel(**item) for item in response["Items"]]


def get_submissions_for_target(
    target_type: str, target_id: str
) -> List[SubmissionModel]:
    response = (
        get_dynamo_db()
        .Table(get_table_name())
        .query(
            IndexName=GSI_SUBMISSION_TARGET,
            KeyConditionExpression=Key(GSI_SUBMISSION_TARGET_PK).eq(target_type)
            & Key(GSI_SUBMISSION_TARGET_SK).eq(target_id),
        )
    )
    return [SubmissionModel(**item) for item in response["Items"]]


def put_submission(model: SubmissionModel) -> SubmissionModel:
    get_dynamo_db().Table(get_table_name()).put_item(
        Item=model.ddict(),
    )
    return model


def update_submission_github_issue(id: int, issue: GitHubIssueModel) -> SubmissionModel:
    submission = get_submission(id)
    get_dynamo_db().Table(get_table_name()).update_item(
        Key={
            MEMBER_PARTITION_KEY: submission.pk,
            MEMBER_SORT_KEY: get_submission_sk(id),
        },
        UpdateExpression="set github_issue = :v",
        ExpressionAttributeValues={":v": issue.ddict()},
    )
    return get_submission(id)
