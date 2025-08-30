from typing import Optional
from uuid import UUID

from asyncpg import ForeignKeyViolationError

from internal.exceptions import (
    CategoryNotFound,
    ForeignKeyException,
    ObjectNotFound,
    TransactionNotFound,
)
from internal.schemas.categories import ResponseCategorySchema
from internal.schemas.transaction import (
    AddTransactionWithUserID,
    RequestGetTransaction,
    RequestUpdateTransacton,
    TransactionResponse,
)
from internal.services.base_service import BaseService


class TransactionService(BaseService):
    async def add_transaction(
        self, data: AddTransactionWithUserID
    ) -> TransactionResponse:
        # пытаемся достать из БД айди категории
        category_schema: Optional[
            ResponseCategorySchema
        ] = await self.db.category.get_one_or_none(
            title=data.category_title, user_id=data.user_id
        )
        if category_schema is None:
            raise CategoryNotFound

        payload = data.model_dump()
        payload.pop("category_title")
        payload["category_id"] = category_schema.category_id

        try:
            result: TransactionResponse = await self.db.transaction.add_to_the_database(
                **payload
            )
        except ForeignKeyViolationError as e:
            raise ForeignKeyException from e

        await self.db.commit()
        return result

    async def get_transactions(
        self, data: RequestGetTransaction, user_id: int, limit: int, offset: int
    ) -> list[TransactionResponse]:
        res: list[
            TransactionResponse
        ] = await self.db.transaction.get_filtered_transaction(
            user_id, limit, offset, **data.model_dump()
        )
        return res

    async def delete_transaction(self, user_id: int, transaction_id: UUID):
        try:
            await self.db.transaction.delete(
                user_id=user_id, transaction_id=transaction_id
            )
        except ObjectNotFound as e:
            raise TransactionNotFound from e

    async def update_transaction(
        self,
        to_update: RequestUpdateTransacton,
        user_id: int,
        transaction_id: UUID,
    ):
        try:
            res: TransactionResponse = await self.db.transaction.update_model(
                to_update, user_id=user_id, transaction_id=transaction_id
            )
        except ObjectNotFound as e:
            raise TransactionNotFound from e
        await self.db.commit()
        return res
