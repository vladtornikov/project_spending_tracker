from asyncpg import ForeignKeyViolationError

from internal.exceptions import ForeignKeyException
from internal.schemas.transaction import (
    AddTransactionWithUserID,
    RequestGetTransaction,
    TransactionResponse,
)
from internal.services.base_service import BaseService


class TransactionService(BaseService):
    async def add_transaction(
        self, data: AddTransactionWithUserID
    ) -> TransactionResponse:
        try:
            result: TransactionResponse = await self.db.transaction.add_to_the_database(
                data.model_dump()
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
