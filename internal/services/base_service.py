import logging
from typing import Optional
from uuid import UUID

from internal.exceptions import CategoryNotFound
from internal.logger import get_logger
from internal.schemas.categories import ResponseCategorySchema
from internal.utils.DB_manager import DbManager


class BaseService:
    logger: logging.Logger = get_logger()

    def __init__(self, db: DbManager):
        self.db = db

    async def check_category_user_id(self, user_id: int, category_id: UUID):
        category_schema: Optional[
            ResponseCategorySchema
        ] = await self.db.category.get_one_or_none(
            category_id=category_id, user_id=user_id
        )
        if category_schema is None:
            raise CategoryNotFound
