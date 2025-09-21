import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler  # mypy: [import-untyped]

from internal.logger import configure_logging, get_logger
from internal.rabbit.publisher_direct_exchange import publish_message

configure_logging()
log = get_logger()


async def delete_transactions(period: int, routing_key: str, task: str):
    await publish_message(routing_key, task=task, period=period)


async def main():
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        delete_transactions,
        trigger="interval",
        minutes=1,
        kwargs={
            "period": 365,
            "routing_key": "beat",
            "task": "beat.delete.old.transactions",
        },
        max_instances=1,  # не запускать конкурентно одну и ту же джобу
    )
    scheduler.start()

    try:
        await asyncio.Event().wait()  # держим процесс живым
    finally:
        scheduler.shutdown()  # для APScheduler v3 метод синхронный


if __name__ == "__main__":
    asyncio.run(main())
