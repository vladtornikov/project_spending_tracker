from datetime import timedelta

from sqlalchemy import delete, func, select

from internal.models_database.transactions import TransactionsModel
from internal.repository.base_repository import BaseRepository
from internal.repository.data_mapper.data_mappers import TransactionDataMapper
from internal.schemas.transaction import TransactionResponse


class TransactionRepository(BaseRepository):
    model = TransactionsModel
    mapper = TransactionDataMapper

    async def get_filtered_transaction(
        self, user_id: int, limit: int, offset: int, **filters
    ) -> list[TransactionResponse]:
        filters_dict = [self.model.user_id == user_id]

        type = filters.get("transaction_type")
        if type is not None:
            filters_dict.append(self.model.transaction_type == type)

        id = filters.get("category_id")
        if id is not None:
            filters_dict.append(self.model.category_id == id)

        start_date = filters.get("start_date")
        if start_date is not None:
            filters_dict.append(self.model.transaction_date >= start_date)

        end_date = filters.get("end_date")
        if end_date is not None:
            filters_dict.append(self.model.transaction_date <= end_date)

        query = (
            select(self.model)
            .filter(*filters_dict)
            .order_by(self.model.transaction_date.desc())
        )
        query = query.limit(limit=limit).offset(offset=offset)

        result = await self.session.execute(query)

        self.logger.info(
            "SQL statement: %s",
            query.compile(compile_kwargs={"literal_binds": True}),
        )

        models = result.scalars().all()
        return [self.mapper.from_SQL_to_pydantic_model(model) for model in models]

    async def delete_old_transaction(self, period: int) -> dict:
        self.logger.info(
            "Начал выполнение фоновой задачи по очистке транзакций, которые хрянятся более %s дней",
            period,
        )
        statement = delete(self.model).where(
            self.model.transaction_date < func.now() - timedelta(days=period)
        )

        res = await self.session.execute(statement)
        rows_counted = res.rowcount
        self.logger.info(
            "Выполнил фоновую задачу, кол-вол удаленных записей - %s", rows_counted
        )
        return {"status": "ok", "rows_affected": rows_counted}
