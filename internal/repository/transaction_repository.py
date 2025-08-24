from sqlalchemy import select

from internal.models_database.transactions import TransactionsModel
from internal.repository.base_repository import BaseRepository
from internal.repository.data_mapper.data_mappers import TransactrionDataMapper
from internal.schemas.transaction import TransactionResponse


class TransactionRepository(BaseRepository):
	model = TransactionsModel
	mapper = TransactrionDataMapper

	async def get_filtered_transaction(self, user_id:int, **filter) -> list[TransactionResponse]:
		filters = [self.model.user_id == user_id]
		if 'transaction_type' in filter:
			filters.append(self.model.transaction_type == filter['transaction_type'])
		if 'category_id' in filter:
			filters.append(self.model.category_id == filter['category_id'])
		if 'start_date' in filter:
			filters.append(self.model.transaction_day_time >= filter['start_date'])
		if 'end_date' in filter:
			filters.append(self.model.transaction_day_time <= filter['start_date'])

		query = (
			select(self.model)
			.filter(*filters)
			.order_by(self.model.transaction_day_time.desc())
		)
		result = await self.session.execute(query)
		models = result.scalars().all()
		return [self.mapper.from_SQL_to_pydantic_model(model) for model in models]