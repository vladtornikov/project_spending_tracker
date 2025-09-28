# from typing import TYPE_CHECKING
#
# import pika
#
# from internal.config import settings
# from internal.logger import configure_logging, get_logger
# from internal.rabbit.config_rabbit_mq import get_connection
#
# if TYPE_CHECKING:
#     from pika.adapters.blocking_connection import BlockingChannel
#
# configure_logging()
# log = get_logger()
#
# MQ_EXCHANGE = settings.rabbit_mq.rmq_exchange
# MQ_ROUTING_KEY = settings.rabbit_mq.rmq_routing_key
#
#
# def declare_queue(channel: "BlockingChannel") -> None:
#     queue = channel.queue_declare(queue=MQ_ROUTING_KEY, durable=True)
#     log.info("Declared queue %r %s", MQ_ROUTING_KEY, queue)
#
#
# def produce_message(channel: "BlockingChannel", idx: int) -> None:
#     message_body = f"New message #{idx:02d}"
#     log.info("Publish message %s", message_body)
#
#     channel.basic_publish(
#         exchange=MQ_EXCHANGE,
#         routing_key=MQ_ROUTING_KEY,
#         body=message_body,
#         properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent),
#     )
#
#     log.warning("Published message %s", message_body)
#
#
# def main():
#     with get_connection() as connection:
#         log.info("Created connection: %s", connection)
#         with connection.channel() as channel:
#             log.info("Created channel: %s", channel)
#             declare_queue(channel=channel)
#             for i in range(1, 10):
#                 produce_message(channel=channel, idx=i)
#
#
# if __name__ == "__main__":
#     try:
#         main()
#     except KeyboardInterrupt:
#         log.warning("Bye!")
