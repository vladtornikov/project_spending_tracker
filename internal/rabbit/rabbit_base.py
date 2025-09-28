from typing import Optional

from aio_pika import connect_robust
from aio_pika.abc import (
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
)

from internal.config import settings
from internal.logger import configure_logging, get_logger


class RabbitException(Exception):
    pass


configure_logging()
log = get_logger()


class RabbitBase:
    def __init__(self):
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel: Optional[AbstractRobustChannel] = None

    @property
    def exchange(self) -> AbstractRobustExchange:
        if self._channel is None:
            raise RabbitException("Please use context manager for Rabbit")
        return self._exchange

    @property
    def channel(self) -> AbstractRobustChannel:
        if self._channel is None:
            raise RabbitException("Please use context manager for Rabbit")
        return self._channel

    async def __aenter__(self):
        self._connection = await connect_robust(
            url=settings.rabbit_mq.rmq_url,
        )
        self._channel = await self._connection.channel()
        self._exchange: AbstractRobustExchange = await self._channel.declare_exchange(
            name=settings.rabbit_mq.rmq_exchange, type="direct", durable=True
        )
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if self._channel and not self._channel.is_closed:
            log.info("Close the RabbitMQ channel")
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            log.info("Close the RabbitMQ connection")
            await self._connection.close()
