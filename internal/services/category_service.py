from uuid import UUID

from asyncpg import ForeignKeyViolationError  # type: ignore[import-untyped]

from internal.exceptions import (
    CategoryNameExists,
    CategoryNotFound,
    ConflictHasTransactions,
    ObjectAlreadyExists,
    ObjectNotFound,
)
from internal.schemas.categories import (
    AddCategoryWithUserId,
    RequestAddCategory,
    ResponseCategorySchema,
)
from internal.services.base_service import BaseService


class CategoryService(BaseService):
    async def get_all_categories(
        self,
        user_id: int,
        limit: int,
        offset: int,
    ) -> list[ResponseCategorySchema]:
        result: list[
            ResponseCategorySchema
        ] = await self.db.category.get_all_filtered_by(limit, offset, user_id=user_id)
        return result

    async def add_category(self, data: AddCategoryWithUserId) -> ResponseCategorySchema:
        try:
            result: ResponseCategorySchema = await self.db.category.add_to_the_database(
                **data.model_dump()
            )
        except ObjectAlreadyExists as e:
            raise CategoryNameExists from e

        await self.db.commit()
        return result

    async def update_category(
        self, updated_data: RequestAddCategory, user_id: int, category_id: UUID
    ) -> ResponseCategorySchema:
        try:
            result: ResponseCategorySchema = await self.db.category.update_model(
                updated_data, user_id=user_id, category_id=category_id
            )
        except ObjectNotFound as e:
            self.logger.exception(
                "Ошибка! Категория с таким id %s и таким юзером %s не найдена",
                category_id,
                user_id,
            )
            raise CategoryNotFound from e

        await self.db.commit()
        return result

    async def delete_category(self, user_id: int, category_id: UUID) -> None:
        try:
            await self.db.category.delete(user_id=user_id, category_id=category_id)
        except ObjectNotFound as e:
            self.logger.exception(
                "Ошибка! Категория с таким id %s и таким юзером %s не найдена",
                category_id,
                user_id,
            )
            raise CategoryNotFound from e
        except ForeignKeyViolationError as e:
            raise ConflictHasTransactions from e

        await self.db.commit()
