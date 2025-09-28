from celery import Celery  # type: ignore[import-untyped]
from celery.schedules import crontab  # type: ignore[import-untyped]

from internal.config import settings
from internal.logger import configure_logging, get_logger

configure_logging()
logger = get_logger()

app = Celery(
    "celery_tasks.celery_init",
    broker="amqp://guest:guest@localhost:5672//",
    backend="rpc://",
    include=["internal.celery_tasks.tasks"],
)