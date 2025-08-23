from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column

from internal.database import BaseORM

from .users import UsersModel


class CategoryTypeEnum(Enum):
	DEBIT = "debit"
	CREDIT = "credit"


class CategoriesModel(BaseORM):
	__tablename__ = "categories"

	category_id: Mapped[UUID] = mapped_column(
		primary_key=True, server_default=func.gen_random_uuid()
	)
	title: Mapped[str]
	description: Mapped[Optional[str]] = mapped_column(nullable=True)
	user_id: Mapped[int] = mapped_column(ForeignKey(UsersModel.id))
	category_type: Mapped[CategoryTypeEnum] = mapped_column(
		ENUM(
			CategoryTypeEnum,
			create_type=False,
			check_first=False,
			inherit_schema=True,
			name="categorytypeenum",
			values_callable=lambda enum_cls: [e.value for e in enum_cls],
		)
	)
	# In order to persist the values and not the names, the Enum.values_callable parameter may be used.
	# The value of this parameter is a user-supplied callable, which is intended to be used with a PEP-435-compliant
	# enumerated class and returns a list of string values to be persisted.
	# For a simple enumeration that uses string values, a callable such as lambda x: [e.value for e in x] is sufficient.
