from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, ForeignKeyConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, NUMERIC, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import BaseORM

from .categories import CategoriesModel, enum_type, CategoryTypeEnum
from .users import UsersModel


class TransactionsModel(BaseORM):
	__tablename__ = "transactions"

	transaction_id: Mapped[UUID] = mapped_column(
		primary_key=True, server_default=func.gen_random_uuid()
	)

	transaction_type: Mapped[CategoryTypeEnum] = mapped_column(enum_type, nullable=False)

	amount: Mapped[Decimal] = mapped_column(
		NUMERIC(14, 2),
		CheckConstraint("amount>=0"),
		nullable=False,
	)

	transaction_day_time: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True), nullable=False
	)

	created_at: Mapped[datetime] = mapped_column(
		TIMESTAMP(timezone=True),
		server_default=func.now(),
		nullable=False,
	)  # server_default - чтобы подсчет выполнялся БД

	description: Mapped[Optional[str]] = mapped_column(nullable=True)
	other_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
	category_id: Mapped[UUID] = mapped_column(nullable=False)
	user_id: Mapped[int] = mapped_column(
		ForeignKey(UsersModel.id, ondelete="RESTRICT", onupdate="CASCADE"),
		nullable=False,
	)

	__table_args__ = (
		ForeignKeyConstraint(
			["category_id", "user_id"],
			[CategoriesModel.category_id, CategoriesModel.user_id],
			ondelete="RESTRICT",
			onupdate="CASCADE",
		),
		ForeignKeyConstraint(
			["category_id", "transaction_type"],
			[CategoriesModel.category_id, CategoriesModel.category_type],
			ondelete="RESTRICT",
			onupdate="CASCADE",
		),
	)
	# It’s important to note that the ForeignKeyConstraint is the only way to define a composite foreign key.
	# While we could also have placed individual ForeignKey objects on both [...] columns,
	# SQLAlchemy would not be aware that these two values should be paired together -
	# it would be two individual foreign key constraints instead of a single composite foreign key
	# referencing two column
