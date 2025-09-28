import uuid
from datetime import date, timedelta

from sqlalchemy import delete, func, select

from internal.models_database.categories import CategoriesModel
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

    async def delete_old_transaction(self, period: int) -> int:
        self.logger.info(
            "Start deleting transactions that last more than %s days",
            period,
        )
        statement = delete(self.model).where(
            self.model.transaction_date < func.now() - timedelta(days=period)
        )

        res = await self.session.execute(statement)
        rows_counted = res.rowcount
        self.logger.info(
            "Successfully deleted transaction(s), amount - %s", rows_counted
        )
        return rows_counted

    async def get_transaction_report_by_period(self, **filters):
        self.logger.info(
            "Start backroung task for generating a report, category_id %r",
            filters["category_id"],
        )

        to_filt = [self.model.category_id == uuid.UUID(filters["category_id"])]

        start_date = filters.get("start_date")
        if start_date is not None:
            start_date = date.fromisoformat(start_date)
            to_filt.append(self.model.transaction_date >= start_date)

        end_date = filters.get("end_date")
        if end_date is not None:
            end_date = date.fromisoformat(end_date)
            to_filt.append(self.model.transaction_date <= end_date)

        total_amount = func.sum(self.model.amount).label("total_amount")
        query = (
            select(
                CategoriesModel.title.label("category_title"),
                total_amount,
            )
            .select_from(self.model)
            .join(
                CategoriesModel, self.model.category_id == CategoriesModel.category_id
            )
            .filter(*to_filt)
            .group_by(CategoriesModel.title)
            .order_by(total_amount.desc())
        )
        result = await self.session.execute(query)
        rows = result.all()
        self.logger.info("RESULT %r", rows)
        return rows
