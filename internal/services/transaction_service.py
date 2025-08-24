from internal.schemas.transaction import AddTransactionWithUserID, TransactionResponse, RequestGetTransaction
from internal.services.base_service import BaseService


class TransactionService(BaseService):
	async def add_transaction(
		self, data: AddTransactionWithUserID
	) -> TransactionResponse:
		result: TransactionResponse = await self.db.transaction.add_to_the_database(
			data.model_dump()
		)
		await self.db.commit()
		return result

	async def get_transactions(self, data: RequestGetTransaction, user_id: int) -> list[TransactionResponse]:
		res: list[TransactionResponse] = \
			await self.db.transaction.get_filtered_transaction(user_id, **data.model_dump())
		return res
