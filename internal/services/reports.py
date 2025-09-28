from internal.rabbit.publisher_direct_exchange import publish_message
from internal.schemas.reports import OneCategoryReport
from internal.services.base_service import BaseService


class ReportsService(BaseService):
    async def one_category_report(self, routing_key: str, data: OneCategoryReport):
        message: dict = data.model_dump()
        await publish_message(
            routing_key, task="reports.generate.monthly_by_category", **message
        )
