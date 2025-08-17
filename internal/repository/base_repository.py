import logging

from asyncpg.exceptions import UniqueViolationError
from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from internal.exceptions import ObjectAlreadyExistsException
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

		self.logger.info(
			"SQL statement: %s",
			add_data_stmt.compile(compile_kwargs={"literal_binds": True}),
		)

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
