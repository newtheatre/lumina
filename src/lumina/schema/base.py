import humps
from pydantic import BaseModel, ConfigDict


def to_camel(string):
    return humps.camelize(string)


class LuminaModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)
