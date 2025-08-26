from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from internal.config import settings

engine = create_async_engine(
    settings.database.DB_URL,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class BaseORM(DeclarativeBase):
    pass
