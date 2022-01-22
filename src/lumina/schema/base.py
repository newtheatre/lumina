import humps
from pydantic import BaseModel


def to_camel(string):
    return humps.camelize(string)


class LuminaModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
