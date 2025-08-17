from typing import Annotated

from fastapi import Depends

from .database import async_session_maker
from .utils.DB_manager import DB_Manager


async def get_db() -> DB_Manager:
	async with DB_Manager(session_factory=async_session_maker) as db:
		yield db


DB_Dep = Annotated[DB_Manager, Depends(get_db)]
