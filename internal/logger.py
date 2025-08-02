import logging

from internal.config import settings

log_format = settings.yaml.logger.format


def configure_logging(level=settings.yaml.logger.level):
	logging.basicConfig(
		level=level,
		datefmt="%Y-%m-%d %H:%M:%S",
		format=log_format,
	)
