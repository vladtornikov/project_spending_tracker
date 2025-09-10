import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from internal.celery_tasks.celery_init import app
from internal.config import settings
from internal.logger import configure_logging
from internal.utils.DB_manager import DB_Manager

logger = configure_logging()


async def cleanup_transactions(period: int) -> dict:
    engine = create_async_engine(
        settings.database.DB_URL,
        pool_pre_ping=True,
    )
    # либо можно сделать с poolclass=NullPool, но мне захотелось попробовать реализовать через закрытие engine
    # просто с NullPool было на курсе Шумейко, и тогда я вообще не понял, для чего это нужно. щас вроде понял))
    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    try:
        async with DB_Manager(session_factory=async_session_maker) as db:
            logger.info("Подключился к БД для очистки (period_days=%s)", period)
            result = await db.transaction.delete_old_transaction(period)
            await db.commit()
            return result
    finally:
        await engine.dispose()
        logger.info(
            "Отключил engine базы данных, при следующей задаче будет создан новый engine"
        )


@app.task(name="cleanup_transactions", bind=True)
def delete_transactions(self, period: int) -> dict:
    logger.info("Выполняю задачу id %r", self.request.id)
    return asyncio.run(cleanup_transactions(period=period))
