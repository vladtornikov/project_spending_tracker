from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from internal.dependencies import DB_Dep, User_id_Dep
from internal.exceptions import CategoryNotFound
from internal.schemas.reports import OneCategoryReport
from internal.services.base_service import BaseService
from internal.services.reports import ReportsService

router = APIRouter(prefix="/api/v1/reports", tags=["Reports"])


@router.get(
    path="/category_id",
    summary="Get transactions report for a specified period",
)
async def get_report_category(
    user_id: User_id_Dep,
    db: DB_Dep,
    filter_query: Annotated[OneCategoryReport, Query()],
):
    if not filter_query.category_id:
        raise CategoryNotFound

    try:
        await BaseService(db).check_category_user_id(
            user_id=user_id,
            category_id=filter_query.category_id,
        )
    except CategoryNotFound as e:
        raise e

    if (
        filter_query.start_date
        and filter_query.end_date
        and filter_query.start_date > filter_query.end_date
    ):
        raise HTTPException(
            status_code=422, detail="start_date не может быть больше end_date"
        )

    await ReportsService(db).one_category_report("transaction_report", filter_query)
