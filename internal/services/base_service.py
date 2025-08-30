import logging

from internal.logger import get_logger
from internal.utils.DB_manager import DB_Manager


class BaseService:
    logger: logging.Logger = get_logger()

    def __init__(self, db: DB_Manager):
        self.db = db
