import json
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from aio_pika import DeliveryMode, Message

from internal.logger import configure_logging, get_logger
from internal.rabbit import RabbitBase

configure_logging()
log = get_logger()


class Producer(RabbitBase):
    @staticmethod
    def json_encode(obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, Decimal):
            return str(obj)
        raise TypeError(f"Type not serializable: {type(obj)}")

    async def produce_message(self, routing_key: str, message: dict):
        message_body = json.dumps(
            message,
            separators=(",", ":"),
            default=self.json_encode,
        ).encode("utf-8")  # в Message должны передаваться bytes

        message_body = Message(
            body=message_body,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        # Messages marked as 'persistent' that are delivered to 'durable' queues will be logged to disk.
        # Durable queues are recovered in the event of a crash, along with any persistent messages they
        # stored prior to the crash.
        log.info("Publish message %r", message_body)

        await self.exchange.publish(
            message=message_body,
            routing_key=routing_key,
        )
        log.warning("Published message %r", message_body)


async def publish_message(routing_key: str, **message):
    async with Producer() as producer:
        await producer.produce_message(routing_key, message)
