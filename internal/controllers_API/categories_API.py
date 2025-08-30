from uuid import UUID

from fastapi import APIRouter

from internal.dependencies import DB_Dep, PaginationDep, User_id_Dep
from internal.exceptions import (
    CategoryNameExists,
    CategoryNotFound,
    ConflictHasTransactions,
)
from internal.logger import logger_dep
from internal.schemas.categories import (
    AddCategoryWithUserId,
    RequestAddCategory,
    ResponseCategorySchema,
)
from internal.services.category_service import CategoryService

router = APIRouter(prefix="/api/v1/categories", tags=["Categories"])


@router.get(
    path="",
    summary="Get list of all categories of the user",
    response_model=list[ResponseCategorySchema],
)
async def get_all_categories(
    pagination: PaginationDep,
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
):
    result: list[ResponseCategorySchema] = await CategoryService(db).get_all_categories(
        user_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )

    logger.info(
        "Got %d categories for user %s (page=%s, per_page=%s)",
        len(result),
        user_id,
        pagination.page,
        pagination.per_page,
    )
    return result


@router.post(path="", summary="Add category", response_model=ResponseCategorySchema)
async def add_category(
    db: DB_Dep, logger: logger_dep, user_id: User_id_Dep, data: RequestAddCategory
):
    try:
        result: ResponseCategorySchema = await CategoryService(db).add_category(
            AddCategoryWithUserId(**data.model_dump(), user_id=user_id)
        )
    except CategoryNameExists:
        raise CategoryNameExists

    logger.info(
        "Successfully add category to the database for user %s, data: %s",
        user_id,
        result.model_dump(),
    )
    return result


# мне вот не нравится, что у меня в ручках put and delete запрос происходит по айди категории
# мне кажется, это неудобно. наверное, можно попробовать реализовать через юзер айди и title
# т.к. в таблице категорий у меня юзер айди и title составляют unique constraint
# и то же самое, наверное, можно сделать с транзакциями. но я не уверен, что это правильный путь, поэтому пока не буду менять))
@router.put(
    path="/{category_id}",
    summary="Update category",
    response_model=ResponseCategorySchema,
)
async def update_category(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    updated_data: RequestAddCategory,
    category_id: UUID,
):
    try:
        result: ResponseCategorySchema = await CategoryService(db).update_category(
            updated_data,
            user_id,
            category_id,
        )
    except CategoryNotFound:
        raise CategoryNotFound

    logger.info("Successfully updated category, new columns %s", result.model_dump())
    return result


@router.delete(path="/{category_id}", summary="Delete category", response_model=dict)
async def delete_category(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    category_id: UUID,
):
    try:
        await CategoryService(db).delete_category(user_id, category_id)
    except CategoryNotFound:
        raise CategoryNotFound
    except ConflictHasTransactions:
        raise ConflictHasTransactions

    logger.info("Successfully deleted category with id %s", category_id)
    return {"status": "success"}
