from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from internal.config import settings

engine = create_async_engine(
    settings.database.DB_URL,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_pre_ping=True,
    # The “pre ping” feature operates on a per-dialect basis either by invoking a DBAPI-specific “ping”
    # method, or if not available will emit SQL equivalent to “SELECT 1”, catching any errors and
    # detecting the error as a “disconnect” situation. If the ping / error check determines that the
    # connection is not usable, the connection will be immediately recycled, and all other pooled
    # connections older than the current time are invalidated, so that the next time they are checked out,
    # they will also be recycled before use
)
async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)


class BaseORM(DeclarativeBase):
    pass
