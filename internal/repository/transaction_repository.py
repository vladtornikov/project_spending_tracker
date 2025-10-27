import csv
import os
import uuid
from datetime import date, timedelta, datetime
from enum import Enum
from pathlib import Path

from sqlalchemy import delete, func, select, and_

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
            "[*] Successfully deleted transaction(s), amount - %s", rows_counted
        )
        return rows_counted

    async def get_transaction_report_by_period(self, **filters):
        self.logger.info(
            "Start backroung task for generating a report for user %r",
            filters["user_id"],
        )

        user_id = filters["user_id"]
        start_date = date.fromisoformat(filters["start_date"])
        end_date = date.fromisoformat(filters["end_date"])

        # total_amount = func.sum(self.model.amount).label("total_amount")
        query = (
            select(
                CategoriesModel.title.label("category_title"),
                self.model.transaction_type,
                self.model.description,
                self.model.other_data,
                self.model.transaction_date,
            )
            .select_from(CategoriesModel)
            .join(
                self.model,
                and_(
                    self.model.category_id == CategoriesModel.category_id,
                    self.model.transaction_date >= start_date,
                    TransactionsModel.transaction_date < end_date,
                ),
            )
            .filter(
                CategoriesModel.user_id == user_id,
            )
            .order_by(
                CategoriesModel.title.asc(),
                self.model.transaction_date.desc().nullslast()
            )
        )
        result = await self.session.execute(query)

        filepath = Path("reports") / ("transactions") / f"{user_id=}"
        fname = f"transactions_{user_id=}_{datetime.now().strftime('%Y-%m-%d')}_{uuid.uuid4().hex[:8]}.csv"

        if not os.path.isdir(filepath):
            filepath.mkdir(parents=True, exist_ok=True)
            new_filepath = filepath / fname
        else:
            new_filepath = filepath / fname

        with open(new_filepath, 'w', newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(result.keys())
            for row in result:
                writer.writerow(
                    [
                        row.category_title,
                        row.transaction_type.value
                        if isinstance(row.transaction_type, Enum)
                        else row.transaction_type,
                        row.description
                        if isinstance(row.description, str)
                        else "без описания",
                        row.other_data,
                        row.transaction_date,
                    ]
                )

        self.logger.info(
            "[*] Success! Saved categories report to path %r",
            new_filepath,
        )

