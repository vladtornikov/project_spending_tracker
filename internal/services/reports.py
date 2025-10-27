from internal.rabbit.publisher_direct_exchange import publish_message
from internal.schemas.reports import SchemaReport
from internal.services.base_service import BaseService


class ReportsService(BaseService):
    async def transaction_report(self, routing_key: str, data: SchemaReport):
        message: dict = data.model_dump()
        await publish_message(routing_key, **message)

    async def cetegories_report(self, routing_key: str, data: SchemaReport):
        message: dict = data.model_dump()
        await publish_message(routing_key, **message)
