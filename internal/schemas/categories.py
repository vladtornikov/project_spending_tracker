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
	def normalize_enum(cls, data: str) -> str:
		return data.strip().lower()


class AddCategoryWithUserId(RequestAddCategory):
	user_id: int


class ResponseCategorySchema(BaseModel):
	model_config = ConfigDict(use_enum_values=True, from_attributes=True)

	category_id: UUID
	title: str
	description: Optional[str] = None
	user_id: int
	category_type: CategoryEnum
