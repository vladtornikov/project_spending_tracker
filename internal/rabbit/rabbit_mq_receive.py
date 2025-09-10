import time
from typing import TYPE_CHECKING

from internal.config import settings
from internal.logger import configure_logging, get_logger
from internal.rabbit.common import EmailUpdatesRabbit

if TYPE_CHECKING:
    from pika.adapters.blocking_connection import BlockingChannel
    from pika.spec import Basic, BasicProperties

configure_logging()
log = get_logger()
MQ_ROUTING_KEY = settings.rabbit_mq.rmq_routing_key


def process_new_message(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.info("Received message: %r", body.decode())

    log.info("Start checking user email: %r", body.decode())
    time.sleep(2)

    channel.basic_ack(delivery_tag=method.delivery_tag)
    log.info(" [x] Finished checking user email, status - ok")


def main():
    with EmailUpdatesRabbit() as rabbit:
        rabbit.consume_messages(
            message_callback=process_new_message,
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
