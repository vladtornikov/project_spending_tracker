import uuid
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, validates

from internal.database import BaseORM

from .categories import CategoriesModel
from .users import UsersModel


class TransactionTypeEnum(Enum):
	DEBIT = "debit"
	CREDIT = "credit"


class TransactionsModel(BaseORM):
	__tablename__ = "transactions"

	transaction_id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
	transaction_type: Mapped[TransactionTypeEnum] = mapped_column(
		SQLEnum(
			TransactionTypeEnum,
			values_callable=lambda enum_cls: [e.value for e in enum_cls],
		)
	)
	# In order to persist the values and not the names, the Enum.values_callable parameter may be used.
	# The value of this parameter is a user-supplied callable, which is intended to be used with a PEP-435-compliant
	# enumerated class and returns a list of string values to be persisted.
	# For a simple enumeration that uses string values, a callable such as lambda x: [e.value for e in x] is sufficient.
	amount: Mapped[Decimal]
	transaction_day_time: Mapped[datetime]
	created_at: Mapped[datetime] = mapped_column(
		server_default=func.now()
	)  # server_default - чтобы подсчет выполнялся БД
	category_id: Mapped[UUID] = mapped_column(ForeignKey(CategoriesModel.category_id))
	description: Mapped[Optional[str]] = mapped_column(nullable=True)
	user_id: Mapped[int] = mapped_column(ForeignKey(UsersModel.id))
	other_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

	@validates("amount")
	def validate_amount(
		self, _: str, amount: int
	) -> int:  # _ is the name of the column, here it is 'amount'
		if amount < 0:
			raise ValueError("amount must be greater or equal to 0")
		return amount
