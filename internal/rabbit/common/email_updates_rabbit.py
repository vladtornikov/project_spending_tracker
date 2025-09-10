from typing import Callable

from pika.adapters.blocking_connection import BlockingChannel
from pika.exchange_type import ExchangeType  # type: ignore[import-untyped]
from pika.spec import Basic, BasicProperties

from internal.config import settings
from internal.logger import configure_logging, get_logger
from internal.rabbit.rabbit_base import RabbitBase

configure_logging()
log = get_logger()


class EmailUpdatesRabbit(RabbitBase):
    channel: BlockingChannel
    exchange = settings.rabbit_mq.email_updates_exchange_name

    def email_updates_exchange(self):
        self.channel.exchange_declare(
            exchange=self.exchange,
            exchange_type=ExchangeType.fanout,
        )

    def declare_queue_for_email_updates(
        self,
        queue_name: str = "",
        exclusive: bool = True,
    ) -> str:
        self.email_updates_exchange()
        queue = self.channel.queue_declare(queue=queue_name, exclusive=exclusive)
        q_name = queue.method.queue
        self.channel.queue_bind(
            exchange=self.exchange,
            queue=q_name,
        )
        return q_name

    def consume_messages(
        self,
        message_callback: Callable[
            [
                BlockingChannel,
                Basic.Deliver,
                BasicProperties,
                bytes,
            ],
            None,
        ],
        queue_name: str = "",
        prefetch_count: int = 1,
    ):
        self.channel.basic_qos(prefetch_count=prefetch_count)
        queue_name = self.declare_queue_for_email_updates(queue_name)
        self.channel.basic_consume(
            queue=queue_name,
            on_message_callback=message_callback,
        )
        log.info(" [*] Waiting for messages. To exit press CTRL+C")
        self.channel.start_consuming()
