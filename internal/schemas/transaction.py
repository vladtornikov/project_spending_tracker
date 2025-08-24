import decimal
from datetime import datetime
from enum import StrEnum
from typing import Annotated, Any, Optional
from uuid import UUID

from pydantic import (
	AwareDatetime,
	BaseModel,
	ConfigDict,
	Field,
	field_validator, model_validator,
)


class TransactionEnum(StrEnum):
	DEBIT = "debit"
	CREDIT = "credit"


class RequestAddTransaction(BaseModel):
	model_config = ConfigDict(use_enum_values=True)

	transaction_type: TransactionEnum
	amount: decimal.Decimal = Annotated[
		decimal.Decimal, Field(ge=0, max_digits=14, decimal_places=2)
	]
	transaction_day_time: AwareDatetime  # чтобы включала часовой пояс
	category_id: UUID
	description: Optional[str] = Field(default=None, max_length=500)
	other_data: Optional[dict[str, Any]] = None

	@field_validator("transaction_type", mode="before")
	@classmethod
	def normalize_enum(cls, data) -> str:
		if isinstance(data, str):
			data = data.strip().lower()
		return data


class AddTransactionWithUserID(RequestAddTransaction):
	user_id: int


class TransactionResponse(AddTransactionWithUserID):
	transaction_id: UUID
	created_at: AwareDatetime  # чтобы включала часовой пояс

class RequestGetTransaction(BaseModel):
	transaction_type: Optional[TransactionEnum] = Field(default=None)
	start_date: Optional[datetime] = Field(default=None)
	end_date: Optional[datetime] = Field(default=None)
	category_id: Optional[UUID] = Field(default=None)

	@field_validator("transaction_type", mode="before")
	@classmethod
	def normalize_enum(cls, data) -> Optional[str]:
		if data is None:
			return data
		if isinstance(data, str):
			data = data.strip().lower()
		return data

	@model_validator(mode="after")
	def check_dates(self):
		if self.start_date and self.end_date and self.start_date > self.end_date:
			raise ValueError('start_date не может быть больше end_date')
		return self