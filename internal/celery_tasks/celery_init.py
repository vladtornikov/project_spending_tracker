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
app.conf.update(result_expires=300)

logger.info("Успешно создал Celery приложение")


app.conf.beat_schedule = {
    "cleanup-transactions": {
        "task": "cleanup_transactions",
        "schedule": settings.celery_beat.schedule
        or crontab(),  # либо через конфиг, либо execute every minute.
        "args": (settings.celery_beat.days_period,),
    }
}
