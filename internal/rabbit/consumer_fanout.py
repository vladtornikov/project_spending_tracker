import time

from pika.adapters.blocking_connection import BlockingChannel
from pika.spec import Basic, BasicProperties

from internal.logger import configure_logging, get_logger
from internal.rabbit.common import EmailUpdatesRabbit

configure_logging()
log = get_logger()


def process_new_message(
    channel: "BlockingChannel",
    method: "Basic.Deliver",
    properties: "BasicProperties",
    body: bytes,
):
    log.info("Update user email for newsletters %r", body)
    time.sleep(2)
    channel.basic_ack(delivery_tag=method.delivery_tag)
    log.info(" [x] Updated user email, status - ok")


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
