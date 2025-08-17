from internal.repository.data_mapper.base_data_mapper import BaseDataMapper
from internal.schemas.auth import SignupResponse


class AuthDataMapper(BaseDataMapper):
	response_schema = SignupResponse
