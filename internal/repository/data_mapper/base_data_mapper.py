from pydantic import BaseModel


class BaseDataMapper:
    response_schema: type[BaseModel]

    @classmethod
    def from_SQL_to_pydantic_model(cls, data):
        return cls.response_schema.model_validate(data, from_attributes=True)
