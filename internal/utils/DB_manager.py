from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.repository.auth_repository import AuthRepository


class DB_Manager:
	def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
		self.session_factory = session_factory

	async def __aenter__(self):
		self.session = self.session_factory()
		self.auth = AuthRepository(self.session)

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
