import asyncio
import json

from aio_pika.abc import AbstractIncomingMessage
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from internal.config import settings
from internal.logger import configure_logging, get_logger
from internal.rabbit.rabbit_base import RabbitBase
from internal.services.rabbit_tasks import RabbitTasks

configure_logging()
log = get_logger()


class Consumer(RabbitBase):
    engine = create_async_engine(
        settings.database.DB_URL,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_pre_ping=True,
    )
    async_session_maker = async_sessionmaker(bind=engine, expire_on_commit=False)

    async def process_new_message(self, message: AbstractIncomingMessage):
        async with message.process():
            log.info(
                "Receive message %r, routing key %r", message.body, message.routing_key
            )
            await RabbitTasks(self.async_session_maker).base_consume(
                json.loads(message.body)
            )
            log.info(" [x] Successfully worked with message %r, status - ok", message.body)

    async def consume_message(self, prefetch_count: int = 1):
        """
        Слушаем ИМЕННУЮ durable-очередь и биндимся ко всем routing_key из конфига.
        Очередь должна существовать до публикаций (на старте воркера).
        Это чтобы, если воркер у нас упал, сообщение не потерялось.
        То есть мы связываем exchange всегда с определенной очередью. Поэтому сообщения не теряеются
        """
        queue_name = settings.rabbit_mq.rmq_queue_name
        await self.channel.set_qos(prefetch_count=prefetch_count)
        queue = await self.channel.declare_queue(name=queue_name, durable=True)

        for routing_key in settings.rabbit_mq.rmq_routing_keys:
            await queue.bind(
                exchange=self.exchange,
                routing_key=routing_key,
            )
            log.info(
                " [*] Bound queue=%r to exchange=%r rk=%r",
                queue_name,
                settings.rabbit_mq.rmq_exchange,
                routing_key,
            )

        await queue.consume(callback=self.process_new_message)
        log.info(
            " [*] Consuming queue=%r (prefetch=%d). CTRL+C to exit.",
            queue_name,
            prefetch_count,
        )
        # Чтобы воркер "висел", а не выходил после выполнения одной таски, держим event loop живым
        await asyncio.Future()

    async def __aexit__(self, exc_type, exc_value, traceback):
        log.info("Close the database engine")
        await self.engine.dispose()
        await super().__aexit__(exc_type, exc_value, traceback)


async def consume():
    async with Consumer() as consumer:
        await consumer.consume_message()


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        log.warning("Close the RabbitMQ consumer")
