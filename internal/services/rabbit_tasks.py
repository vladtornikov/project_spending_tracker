from typing import Any, Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.logger import configure_logging, get_logger
from internal.utils.DB_manager import DbManager

configure_logging()
log = get_logger()


class RabbitTasks:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

        self.handlers: dict[str, Callable[[dict], Any]] = {
            "transaction_report": self.handle_transaction_report,
            "beat": self.handle_cleanup,
            "categories_report": self.handle_categories_report,
        }

    async def base_consume(self, routing_key: str, payload: dict):
        handler = self.handlers.get(routing_key)
        if not handler:
            raise ValueError(f"No handler for {routing_key=}")

        async with DbManager(session_factory=self.session_factory) as db:
            result = await handler(db, payload)
            return result

    async def handle_transaction_report(self, db: DbManager, parameters: dict):
        await db.transaction.get_transaction_report_by_period(**parameters)

    async def handle_categories_report(self, db: DbManager, parameters: dict):
        await db.category.get_report_categories(**parameters)

    async def handle_cleanup(self, db: DbManager, parameters: dict):
        result: int = await db.transaction.delete_old_transaction(
            period=parameters["period"]
        )
        await db.commit()
        log.info("Background_task_completed, deleted rows - %s", result)
        return result
