import logging
from typing import Optional

from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.exceptions import ObjectAlreadyExistsException, ObjectNotFoundException
from internal.logger import get_logger

from .data_mapper.base_data_mapper import BaseDataMapper


class BaseRepository:
	model = None
	logger: logging.Logger = get_logger()
	mapper: BaseDataMapper = None

	def __init__(self, session: AsyncSession):
		self.session = session

	async def add_to_the_database(self, data: dict) -> BaseModel:
		add_data_stmt = insert(self.model).values(**data).returning(self.model)

		# self.logger.info(
		# 	"SQL query: %s",
		# 	add_data_stmt.compile(compile_kwargs={"literal_binds": True}),
		# )

		try:
			result = await self.session.execute(add_data_stmt)
		except IntegrityError as ex:
			if isinstance(ex.orig.__cause__, UniqueViolationError):
				self.logger.exception(
					"Не удалось добавить данные в базу, входные данные: %s", data
				)
				raise ObjectAlreadyExistsException from ex

			else:
				self.logger.exception(
					"Незнакомая ошибка: не удалось добавить данные в БД, входные данные: %s",
					data,
				)
				raise ex
		model = result.scalar_one()
		return self.mapper.from_SQL_to_pydantic_model(model)

	async def get_one_or_none(self, **filter_by: dict) -> Optional[BaseModel]:
		query = select(self.model).filter_by(**filter_by)

		self.logger.info(
			"SQL query: %s",
			query.compile(compile_kwargs={"literal_binds": True}),
		)

		result = await self.session.execute(query)
		model = result.scalar_one_or_none()

		if model is None:
			return None

		return self.mapper.from_SQL_to_pydantic_model(model)

	async def get_all_filtered_by(
		self,
		limit: Optional[int] = None,
		offset: Optional[int] = None,
		**filter_by: dict,
	) -> list[BaseModel]:
		query = select(self.model).filter_by(**filter_by)
		if limit is not None:
			query = query.limit(limit)
		if offset is not None:
			query = query.offset(offset)

		self.logger.info(
			"SQL statement: %s",
			query.compile(compile_kwargs={"literal_binds": True}),
		)

		result = await self.session.execute(query)
		models = result.scalars().all()
		return [self.mapper.from_SQL_to_pydantic_model(model) for model in models]

	async def update_model(
		self, updated_data: BaseModel, exclude_unset: bool = False, **filter_by: dict
	) -> BaseModel:
		statement = (
			update(self.model)
			.filter_by(**filter_by)
			.values(**updated_data.model_dump(exclude_unset=exclude_unset))
			.returning(self.model)
		)

		self.logger.info(
			"SQL statement: %s",
			statement.compile(compile_kwargs={"literal_binds": True}),
		)

		try:
			result = await self.session.execute(statement)

		except IntegrityError as ex:
			if isinstance(ex.orig.__cause__, UniqueViolationError):
				self.logger.exception(
					"Не удалось добавить данные в базу, входные данные: %s", filter_by
				)
				raise ObjectAlreadyExistsException from ex

		model = result.scalar_one_or_none()
		if not model:
			self.logger.error(
				"Ошибка! Не удалось найти данные в БД с такими входными данными %s",
				filter_by,
			)
			raise ObjectNotFoundException
		return self.mapper.from_SQL_to_pydantic_model(model)

	async def delete(self, **filter_by: dict) -> None:
		statement = delete(self.model).filter_by(**filter_by).returning(self.model)

		self.logger.info(
			"SQL statement: %s",
			statement.compile(compile_kwargs={"literal_binds": True}),
		)
		result = await self.session.execute(statement)
		model = result.scalar_one_or_none()
		if not model:
			self.logger.error(
				"Ошибка! Не удалось найти данные в БД с такими входными данными %s",
				filter_by,
			)
			raise ObjectNotFoundException
