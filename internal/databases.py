from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from internal.config import settings

engine = create_async_engine(
	settings.env.DB_URL,
	pool_size=settings.env.pool_size,
	max_overflow=settings.env.max_overflow,
)
async_session_maker = async_sessionmaker(bind=engine, expire_in_commit=False)


async def get_db_session() -> AsyncSession:
	async with async_session_maker() as session:
		yield session


DB_Dep = Annotated[AsyncSession, Depends(get_db_session)]


class BaseORM(DeclarativeBase):
	pass
