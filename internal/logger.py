import logging

from internal.config import settings

log_format = settings.yaml.logger.format
date_format = settings.yaml.logger.date_format


def configure_logging(level=settings.yaml.logger.level):
	logging.basicConfig(
		level=level,
		datefmt=date_format,
		format=log_format,
	)
