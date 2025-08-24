from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import BaseORM

from .users import UsersModel


class CategoryTypeEnum(Enum):
	DEBIT = "debit"
	CREDIT = "credit"

# чтобы можно было создать пару transaction_type==category_type, внешний ключ

enum_type = ENUM(
	CategoryTypeEnum,
	name='category_transaction_enum',
	create_type=False,
	check_first=False,
	inherit_schema=True,
	values_callable=lambda enum_cls: [e.value for e in enum_cls],
)

# In order to persist the values and not the names, the Enum.values_callable parameter may be used.
	# The value of this parameter is a user-supplied callable, which is intended to be used with a PEP-435-compliant
	# enumerated class and returns a list of string values to be persisted.
	# For a simple enumeration that uses string values, a callable such as lambda x: [e.value for e in x] is sufficient

class CategoriesModel(BaseORM):
	__tablename__ = "categories"

	category_id: Mapped[UUID] = mapped_column(
		primary_key=True, server_default=func.gen_random_uuid()
	)
	title: Mapped[str]
	description: Mapped[Optional[str]] = mapped_column(nullable=True)
	user_id: Mapped[int] = mapped_column(
		ForeignKey(UsersModel.id, ondelete="RESTRICT", onupdate="CASCADE"),
		nullable=False,
	)
	category_type: Mapped[CategoryTypeEnum] = mapped_column(enum_type, nullable=False)

	__table_args__ = (
		UniqueConstraint("category_id", "user_id"),
		UniqueConstraint("category_id", "category_type"),
		UniqueConstraint("user_id", "title"),
	)
	# 'user_id', 'title' - это бизнес-ограничение. мы не хотим, чтобы у одного пользователя
	# были категории с одинаковым названием

	# однако category_id', 'user_id' и 'category_id', 'category_type' нужны для того,
	# чтобы внешние ключи таблицы transactions ОДНОВРЕМЕННО ссылались на заданные поля в таблице категорий

	# из документации:
	# A foreign key must reference columns that EITHER ARE A PRIMARY KEY OR FORM A UNIQUE CONSTRAINT,
	# or are columns from a non-partial unique index
	# для того, чтобы у нас таблица transactions ссылалась сразу на два ключа одновременно,
	# нужно прописать UniqueConstraint для столбцов
