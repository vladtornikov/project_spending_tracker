import logging
import sys
from typing import Annotated, Optional

from fastapi import Depends

from internal.config import settings


def configure_logging(level: Optional[str] = settings.logger.level) -> logging.Logger:
	logging.basicConfig(
		level=level,
		format=settings.logger.format,
		datefmt=settings.logger.date_format,
		stream=sys.stdout,
	)
	return get_logger()


# создаем эту функцию для DI, чтобы каждый раз у нас не вызывался logger.basicConfig из configure_logging #noqa: E501
def get_logger() -> logging.Logger:
	return logging.getLogger("app")


logger_dep = Annotated[logging.Logger, Depends(get_logger)]
