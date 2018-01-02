import datetime
import uuid

from pynamodb.attributes import UnicodeAttribute, UTCDateTimeAttribute
from pynamodb.models import Model

from . import settings


class LogModel(Model):
    """
    Dump stuff in a log
    """

    class Meta:
        table_name = f"lumina-{settings.STAGE}_log"
        host = settings.DYNAMO_DB_HOST
        region = settings.DYNAMO_DB_REGION

    uuid = UnicodeAttribute(hash_key=True)
    timestamp = UTCDateTimeAttribute(range_key=True)
    message = UnicodeAttribute()

    def __init__(self, message: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.uuid = str(uuid.uuid4())
        self.timestamp = datetime.datetime.now()
        self.message = message


def create_tables() -> int:
    count = 0
    if not LogModel.exists():
        LogModel.create_table(read_capacity_units=1, write_capacity_units=1)
        count += 1
    return count
