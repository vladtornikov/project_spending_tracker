import logging
from typing import Optional

from internal.logger import get_logger
from internal.utils.DB_manager import DB_Manager


class BaseService:
	logger: logging.Logger = get_logger()

	def __init__(self, db: Optional[DB_Manager] = None):
		self.db = db
