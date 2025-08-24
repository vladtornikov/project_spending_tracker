from fastapi import APIRouter

from internal.dependencies import DB_Dep, User_id_Dep, PaginationParams
from internal.logger import logger_dep
from internal.schemas.transaction import (
	AddTransactionWithUserID,
	RequestAddTransaction,
	TransactionResponse, RequestGetTransaction,
)
from internal.services.transaction_service import TransactionService

router = APIRouter(prefix="/api/v1", tags=["Transactions"])


@router.post(
	"/transactions",
	summary="Create new transaction",
	response_model=TransactionResponse,
)
async def create_new_transaction(
	db: DB_Dep, logger: logger_dep, user_id: User_id_Dep, data: RequestAddTransaction
):
	result: TransactionResponse = await TransactionService(db).add_transaction(
		AddTransactionWithUserID(**data.model_dump(), user_id=user_id)
	)
	logger.info(
		"Successfully add transaction to the database for user %s, data: %s",
		user_id,
		result.model_dump(),
	)
	return result

@router.get(
	'/transactions',
	summary='Get transactions',
)
async def get_transaction(
		pagination: PaginationParams,
		db: DB_Dep,
		logger: logger_dep,
		user_id: User_id_Dep,
		data: RequestGetTransaction
):
	res = await TransactionService(db).get_transactions(data, user_id)
	return res