import time

from internal.config import settings
from internal.logger import configure_logging, get_logger
from internal.rabbit.common import EmailUpdatesRabbit
from internal.rabbit.config_rabbit_mq import connection_params

configure_logging()
log = get_logger()


MQ_ROUTING_KEY = settings.rabbit_mq.rmq_routing_key


class Producer(EmailUpdatesRabbit):
    def produce_message(self, idx: int):
        message_body = f"New message #{idx}"
        log.info("Publish message %r", message_body)

        self.channel.basic_publish(
            exchange=settings.rabbit_mq.email_updates_exchange_name,
            routing_key="",
            body=message_body,
        )
        log.warning("Published message %r", message_body)


def main():
    with Producer(connection_params) as producer:
        producer.email_updates_exchange()  # надо установить exchange
        for idx in range(1, 6):
            producer.produce_message(idx=idx)
            time.sleep(0.5)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log.warning("Bye!")
