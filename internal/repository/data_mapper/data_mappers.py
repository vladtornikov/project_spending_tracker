from internal.repository.data_mapper.base_data_mapper import BaseDataMapper
from internal.schemas.auth import SignupResponse
from internal.schemas.categories import ResponseCategorySchema


class AuthDataMapper(BaseDataMapper):
	response_schema = SignupResponse


class CategoryDataMapper(BaseDataMapper):
	response_schema = ResponseCategorySchema
