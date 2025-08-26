import decimal
from datetime import date
from enum import StrEnum
from typing import Annotated, Any, Optional
from uuid import UUID

from pydantic import (
    AwareDatetime,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
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
    transaction_date: date
    category_id: UUID
    description: Optional[str] = Field(default=None, max_length=500)
    other_data: Optional[dict[str, Any]] = None

    @field_validator("transaction_type", mode="before")
    @classmethod
    def normalize_enum(cls, data) -> Optional[str]:
        if data is None:
            return data
        if isinstance(data, str):
            data = data.strip().lower()
        return data

    @field_validator("transaction_date", mode="after")
    @classmethod
    def check_date(cls, trns_date: date) -> date:
        if trns_date > date.today():
            raise ValueError("Введенная дата не может быть в будущем")
        return trns_date


class AddTransactionWithUserID(RequestAddTransaction):
    user_id: int


class TransactionResponse(AddTransactionWithUserID):
    transaction_id: UUID
    created_at: AwareDatetime  # чтобы включала часовой пояс


class RequestGetTransaction(BaseModel):
    transaction_type: Optional[TransactionEnum] = Field(default=None)
    start_date: Optional[date] = Field(default=None)
    end_date: Optional[date] = Field(default=None)
    category_id: Optional[UUID] = Field(default=None)
