from typing import Annotated

from fastapi import Depends, Query
from fastapi.security import (
	HTTPBearer,
	OAuth2PasswordBearer,
)
from pydantic import BaseModel

from .database import async_session_maker
from .exceptions import (
	ExpiredTokenHTTPException,
	IncorrectTokenException,
	IncorrectTokenHTTPException,
	TokenExpiredException,
)
from .services.auth_service import AuthService
from .utils.DB_manager import DB_Manager


async def get_db() -> DB_Manager:
	async with DB_Manager(session_factory=async_session_maker) as db:
		yield db


DB_Dep = Annotated[DB_Manager, Depends(get_db)]

http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/signin/")


def get_token(
	# credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
	token: str = Depends(oauth2_scheme),
) -> str:
	# return credentials.credentials
	return token


def get_current_user_id(access_token=Depends(get_token)) -> int:
	try:
		decoded_token: dict = AuthService().decode_token(access_token)

	except TokenExpiredException as e:
		raise ExpiredTokenHTTPException from e

	except IncorrectTokenException as e:
		raise IncorrectTokenHTTPException from e

	return int(decoded_token.get("sub"))


User_id_Dep = Annotated[int, Depends(get_current_user_id)]


class PaginationParams(BaseModel):
	page: Annotated[int, Query(default=1, ge=1)]
	per_page: Annotated[int | None, Query(6, ge=1, lt=20)]


PaginationDep = Annotated[PaginationParams, Depends()]
