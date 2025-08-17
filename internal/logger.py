import logging
import sys
from typing import Annotated, Optional

from fastapi import Depends
from pythonjsonlogger.json import JsonFormatter

from internal.config import settings


def configure_logging(level: Optional[str] = None) -> logging.Logger:
	if level is None:
		level = settings.logger.level

	if settings.environment == "development":
		formatter = logging.Formatter(
			fmt=settings.logger.format, datefmt=settings.logger.date_format
		)

	else:
		formatter = JsonFormatter(
			fmt=settings.logger.format,
			datefmt=settings.logger.date_format,
			rename_fields={
				"asctime": "timestamp",
				"filename": "service",
				"lineno": "line",
				"levelname": "level",
			},
		)

	handler = logging.StreamHandler(stream=sys.stdout)
	handler.setFormatter(formatter)
	logging.basicConfig(
		level=level,
		handlers=[handler],
	)
	return get_logger()


# создаем эту функцию для DI, чтобы каждый раз у нас не вызывался logger.basicConfig из configure_logging #noqa: E501
def get_logger() -> logging.Logger:
	return logging.getLogger("app")


logger_dep = Annotated[logging.Logger, Depends(get_logger)]
