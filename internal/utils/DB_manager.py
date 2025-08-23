from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.repository.auth_repository import AuthRepository
from internal.repository.category_repository import CategoryRepository


class DB_Manager:
	def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
		self.session_factory = session_factory

	async def __aenter__(self):
		self.session = self.session_factory()
		self.auth = AuthRepository(self.session)
		self.category = CategoryRepository(self.session)

		return self

	async def __aexit__(self, exc_type, exc_value, traceback):
		try:
			if exc_type is None:
				await self.session.commit()
			else:
				await self.session.rollback()
		finally:
			await self.session.close()
		return False

	async def commit(self):
		await self.session.commit()
