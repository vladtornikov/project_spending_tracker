# import decimal
# from datetime import datetime
# from enum import Enum
# from typing import Optional, Any
#
# from pydantic import BaseModel, field_validator, ConfigDict, condecimal, Field, AwareDatetime
#
#
# class TransactionEnum(Enum):
#     DEBIT = 'debit'
#     CREDIT = 'credit'
#
#
# class AddTransaction(BaseModel):
#     model_config = ConfigDict(use_enum_values=True)
#
#     transaction_type: TransactionEnum
#     amount: decimal.Decimal = Field(condecimal(ge=0), max_digits=14, decimal_places=2)
#     transaction_day_time: AwareDatetime
#     description: Optional[str] = Field(default=None, max_length=500)
#     other_data: Optional[dict[str, Any]] = None
#
#     @field_validator('transaction_type', mode='before')
#     @classmethod
#     def normalize(cls, v):
#         if isinstance(v, str):
#             v = v.strip().lower()
#         return v
