from enum import StrEnum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CategoryEnum(StrEnum):
	DEBIT = "debit"
	CREDIT = "credit"


class RequestAddCategory(BaseModel):
	model_config = ConfigDict(use_enum_values=True)

	title: str = Field(min_length=1, max_length=100)
	description: Optional[str] = Field(default=None, max_length=100)
	category_type: CategoryEnum

	@field_validator("category_type", mode="before")
	@classmethod
	def normalize_enum(cls, data) -> str:
		if isinstance(data, str):
			data = data.strip().lower()
		return data


class AddCategoryWithUserId(RequestAddCategory):
	user_id: int


class ResponseCategorySchema(AddCategoryWithUserId):
	category_id: UUID
