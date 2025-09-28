import pika

from internal.config import settings

connection_params = pika.ConnectionParameters(
    host=settings.rabbit_mq.rmq_host,
    port=settings.rabbit_mq.rmq_port,
    credentials=pika.PlainCredentials(
        settings.rabbit_mq.rmq_user, settings.rabbit_mq.rmq_password
    ),
)


def get_connection() -> pika.BlockingConnection:
    return pika.BlockingConnection(
        parameters=connection_params,
    )
