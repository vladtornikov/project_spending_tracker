from collections.abc import AsyncGenerator
from enum import StrEnum
from typing import Annotated

from fastapi import Depends
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
)
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from internal.utils.DB_manager import DB_Manager

from .database import async_session_maker
from .exceptions import (
    IncorrectToken,
    TokenExpired,
)
from .services.auth_service import AuthService


async def get_db() -> AsyncGenerator[AsyncSession | None]:
    async with DB_Manager(session_factory=async_session_maker) as db:
        yield db


DB_Dep = Annotated[DB_Manager, Depends(get_db)]


http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/signin/", auto_error=False)


def get_token(
    # credentials: HTTPAuthorizationCredentials = Depends(http_bearer)
    token: str = Depends(oauth2_scheme),
) -> str:
    # return credentials.credentials
    return token


def get_current_user_id(access_token=Depends(get_token)) -> int:
    try:
        decoded_token: dict = AuthService(DB_Manager).decode_token(access_token)

    except TokenExpired as e:
        raise e

    except IncorrectToken as e:
        raise e

    sub = decoded_token.get("sub")

    if not isinstance(sub, (str, int)):
        raise IncorrectToken

    try:
        return int(sub)
    except ValueError:
        raise IncorrectToken from ValueError


User_id_Dep = Annotated[int, Depends(get_current_user_id)]


class PaginationParams(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=6, ge=1, lt=20)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


PaginationDep = Annotated[PaginationParams, Depends()]


class TransactionEnum(StrEnum):
    DEBIT = "debit"
    CREDIT = "credit"


TransactionTypeDep = Annotated[TransactionEnum, Depends()]
