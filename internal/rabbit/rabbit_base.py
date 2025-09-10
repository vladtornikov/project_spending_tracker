from typing import Optional

import pika
from pika.adapters.blocking_connection import BlockingChannel

from internal.rabbit.config_rabbit_mq import connection_params


class RabbitException(Exception):
    pass


class RabbitBase:
    def __init__(
        self, connection_params: pika.ConnectionParameters = connection_params
    ):
        self._connection_params = connection_params
        self._connection: Optional[pika.BlockingConnection] = None
        self._channel: Optional[BlockingChannel] = None

    @property
    def channel(self) -> BlockingChannel:
        if self._channel is None:
            raise RabbitException("Please use context manager for Rabbit")
        return self._channel

    def __enter__(self):
        self._connection = pika.BlockingConnection(self._connection_params)
        self._channel = self._connection.channel()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self._channel.is_open:
            self._channel.close()
        if self._connection.is_open:
            self._connection.close()
