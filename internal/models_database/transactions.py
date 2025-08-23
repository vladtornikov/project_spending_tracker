from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM, NUMERIC, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column, validates

from internal.database import BaseORM

from .categories import CategoriesModel
from .users import UsersModel


class TransactionTypeEnum(Enum):
	DEBIT = "debit"
	CREDIT = "credit"


class TransactionsModel(BaseORM):
	__tablename__ = "transactions"

	transaction_id: Mapped[UUID] = mapped_column(
		primary_key=True, server_default=func.gen_random_uuid()
	)

	transaction_type: Mapped[TransactionTypeEnum] = mapped_column(
		ENUM(
			TransactionTypeEnum,
			create_type=False,
			checkfirst=True,
			inherit_schema=True,
			name="transactiontypeenum",
			values_callable=lambda enum_cls: [e.value for e in enum_cls],
		)
	)
	# In order to persist the values and not the names, the Enum.values_callable parameter may be used.
	# The value of this parameter is a user-supplied callable, which is intended to be used with a PEP-435-compliant
	# enumerated class and returns a list of string values to be persisted.
	# For a simple enumeration that uses string values, a callable such as lambda x: [e.value for e in x] is sufficient.

	amount: Mapped[Decimal] = mapped_column(NUMERIC(14, 2), nullable=False)

	transaction_day_time: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)

	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		nullable=False,
	)  # server_default - чтобы подсчет выполнялся БД

	category_id: Mapped[UUID | None] = mapped_column(
		ForeignKey(
			CategoriesModel.category_id, ondelete="SET NULL", onupdate="CASCADE"
		),
		nullable=True,
	)

	description: Mapped[Optional[str]] = mapped_column(nullable=True)

	user_id: Mapped[int | None] = mapped_column(
		ForeignKey(UsersModel.id, ondelete="SET NULL", onupdate="CASCADE"),
		nullable=True,
	)

	other_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

	@validates("amount")
	def validate_amount(
		self, _: str, amount: Decimal
	) -> Decimal:  # _ is the name of the column, here it is 'amount'
		if amount < 0:
			raise ValueError("amount must be greater or equal to 0")
		return amount
