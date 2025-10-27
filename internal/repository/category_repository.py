import csv
import os
import uuid
from datetime import date, datetime
from enum import Enum
from pathlib import Path

from sqlalchemy import and_, func, select
from sqlalchemy.sql.functions import coalesce

from internal.models_database.categories import CategoriesModel
from internal.models_database.transactions import TransactionsModel
from internal.repository.base_repository import BaseRepository
from internal.repository.data_mapper.data_mappers import CategoryDataMapper


class CategoryRepository(BaseRepository):
    model = CategoriesModel
    mapper = CategoryDataMapper

    async def get_report_categories(self, **filters):
        self.logger.info(
            "Start backroung task for generating categories report for user %r",
            filters["user_id"],
        )

        user_id = filters["user_id"]
        start_date = date.fromisoformat(filters["start_date"])
        end_date = date.fromisoformat(filters["end_date"])

        total_amount = coalesce(func.sum(TransactionsModel.amount), 0).label(
            "total_amount"
        )
        query = (
            select(
                self.model.title,
                self.model.description,
                self.model.category_type,
                total_amount,
            )
            .select_from(self.model)
            .join(
                TransactionsModel,
                and_(
                    TransactionsModel.category_id == self.model.category_id,
                    TransactionsModel.transaction_date >= start_date,
                    TransactionsModel.transaction_date < end_date,
                ),
                isouter=True,
            )
            .filter(self.model.user_id == user_id)
            .group_by(self.model.category_id)
            .order_by(total_amount.desc())
        )
        result = await self.session.execute(query)

        filepath = Path("reports") / ("categories") / f"{user_id=}"
        fname = f"categories_{user_id=}_{datetime.now().strftime('%Y-%m-%d')}_{uuid.uuid4().hex[:8]}.csv"

        if not os.path.isdir(filepath):
            filepath.mkdir(parents=True, exist_ok=True)
            new_filepath = filepath / fname
        else:
            new_filepath = filepath / fname

        with open(new_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="\t", quoting=csv.QUOTE_NONNUMERIC)
            writer.writerow(result.keys())
            for row in result:
                writer.writerow(
                    [
                        row.title,
                        row.description
                        if isinstance(row.description, str)
                        else "без описания",
                        row.category_type.value
                        if isinstance(row.category_type, Enum)
                        else row.category_type,
                        row.total_amount,
                    ]
                )

        self.logger.info(
            "[*] Success! Saved categories report to path %r",
            new_filepath,
        )