import logging

from internal.utils.DB_manager import DB_Manager


class BaseService:
	def __init__(self, db: DB_Manager, logger: logging.Logger):
		self.db = db
		self.logger = logger
