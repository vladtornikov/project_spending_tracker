from typing import Annotated

from fastapi import APIRouter, Query

from internal.dependencies import DB_Dep, User_id_Dep
from internal.exceptions import CategoryNotFound
from internal.schemas.reports import SchemaReport, OneCategoryReport
from internal.services.base_service import BaseService
from internal.services.reports import ReportsService

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get(
    path="/transactions",
    summary="Get transactions report for a specified period",
)
async def get_report_category(
    user_id: User_id_Dep,
    db: DB_Dep,
    filter_query: Annotated[SchemaReport, Query()],
):

    filter_query_for_rabbit = SchemaReport(
        start_date=filter_query.start_date,
        end_date=filter_query.end_date,
        user_id=user_id,
    )
    await ReportsService(db).transaction_report(
        "transaction_report", filter_query_for_rabbit
    )

    return 'Ваш запрос получен, находится в обработке'

@router.get(
    path="/categories",
    summary="Get report aggregated by categories",
)
async def get_aggregated_report_category(
    user_id: User_id_Dep, db: DB_Dep, filter_query: Annotated[SchemaReport, Query()]
):
    filter_query_for_rabbit = SchemaReport(
        start_date=filter_query.start_date,
        end_date=filter_query.end_date,
        user_id=user_id,
    )
    await ReportsService(db).cetegories_report(
        "categories_report", filter_query_for_rabbit
    )

    return 'Ваш запрос получен, находится в обработке'