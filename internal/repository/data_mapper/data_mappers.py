from internal.repository.data_mapper.base_data_mapper import BaseDataMapper
from internal.schemas.auth import SignupResponse
from internal.schemas.categories import ResponseCategorySchema
from internal.schemas.transaction import TransactionResponse


class AuthDataMapper(BaseDataMapper):
    response_schema = SignupResponse


class CategoryDataMapper(BaseDataMapper):
    response_schema = ResponseCategorySchema


class TransactionDataMapper(BaseDataMapper):
    response_schema = TransactionResponse
