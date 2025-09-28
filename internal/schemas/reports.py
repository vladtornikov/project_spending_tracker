from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class OneCategoryReport(BaseModel):
    category_id: UUID
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)

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
