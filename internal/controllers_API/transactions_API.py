from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from internal.dependencies import DB_Dep, PaginationDep, User_id_Dep
from internal.exceptions import (
    CategoryNotFound,
    ForeignKeyException,
    TransactionNotFound,
)
from internal.logger import logger_dep
from internal.schemas.transaction import (
    AddTransactionWithUserID,
    RequestAddTransaction,
    RequestGetTransaction,
    RequestUpdateTransacton,
    TransactionEnum,
    TransactionResponse,
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
    try:
        result: TransactionResponse = await TransactionService(db).add_transaction(
            AddTransactionWithUserID(**data.model_dump(), user_id=user_id)
        )
    except ForeignKeyException as e:
        raise e
    except CategoryNotFound as e:
        raise e

    logger.info(
        "Successfully add transaction to the database for user %s, data: %s",
        user_id,
        result.model_dump(),
    )
    return result


@router.get(
    "/transactions",
    summary="Get transactions",
)
async def get_transaction(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    pagination: PaginationDep = Query(),
    transaction_type: TransactionEnum = Query(None),
    category_id: UUID | None = Query(None),
    start_date: datetime | None = Query(None),
    end_date: datetime | None = Query(None),
):
    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=422, detail="start_date не может быть больше end_date"
        )

    data = RequestGetTransaction(
        transaction_type=transaction_type,
        category_id=category_id,
        start_date=start_date,
        end_date=end_date,
    )
    res = await TransactionService(db).get_transactions(
        data,
        user_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return res


@router.put("/transactions/{transaction_id}", summary="Update transaction")
async def update_transaction(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    transaction_id: UUID,
    to_update: RequestUpdateTransacton,
):
    try:
        result: TransactionResponse = await TransactionService(db).update_transaction(
            to_update, user_id, transaction_id
        )
    except TransactionNotFound as e:
        raise e
    return result


@router.delete("/transactions/{transaction_id}", summary="Delete transaction")
async def delete_transaction(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    transaction_id: UUID,
):
    try:
        await TransactionService(db).delete_transaction(user_id, transaction_id)
    except TransactionNotFound as e:
        raise e
    return {"status": "ok"}
