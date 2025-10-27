from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class SchemaReport(BaseModel):
    user_id: Optional[int] = Field(default=None)
    start_date: date
    end_date: date

    @field_validator("start_date", mode="after")
    @classmethod
    def check_start_date(cls, start_date: date) -> date:
        if start_date > date.today():
            raise ValueError("Введенная дата не может быть в будущем")
        return start_date

    @field_validator("end_date", mode="after")
    @classmethod
    def check_end_date(cls, end_date: date) -> date:
        if end_date > date.today():
            raise ValueError("Введенная дата не может быть в будущем")
        return end_date

    @model_validator(mode="after")
    def check_range(self):
        if self.start_date > self.end_date:
            raise ValueError("start_date не может быть больше end_date")
        return self


class OneCategoryReport(SchemaReport):
    category_id: UUID
