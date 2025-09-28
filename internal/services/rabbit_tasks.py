from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from internal.constants import RabbitTasksConstant
from internal.logger import configure_logging, get_logger
from internal.utils.DB_manager import DbManager

configure_logging()
log = get_logger()


class RabbitTasks:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    async def base_consume(self, parameters: dict):
        async with DbManager(session_factory=self.session_factory) as db:
            if parameters.get("task") == RabbitTasksConstant.REPORTS_CATEGORY:
                await db.transaction.get_transaction_report_by_period(**parameters)

            elif parameters.get("task") == RabbitTasksConstant.BEAT_DELETE_TRANSACTION:
                result: int = await db.transaction.delete_old_transaction(
                    period=parameters["period"]
                )
                await db.commit()
                log.info(
                    "Background_task_completed, deleted rows - %s", result
                )
                return result
