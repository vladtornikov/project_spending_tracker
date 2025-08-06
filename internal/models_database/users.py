from datetime import date
from typing import Optional

from internal.databases import BaseModel
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

class UsersModel(BaseModel):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(unique=True)
    hashed_password: Mapped[str]
    fullname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    birthday: Mapped[Optional[date]] = mapped_column(nullable=True)
