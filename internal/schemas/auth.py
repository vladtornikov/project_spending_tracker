import re
from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator


class OptionalColumns(BaseModel):
    fullname: Optional[str] = None
    birthday: Optional[str] = None

    @field_validator('birth_date', check_fields=False)
    @classmethod
    def check_data(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
            raise ValueError('Date must be in a format year-month-day, e.g. 2000-01-31')
        try:
            data_value = datetime.fromisoformat(value)
        except ValueError:
            raise ValueError('Your date is wrong')
        if data_value > datetime.today():
            raise ValueError('Date must be less or equal to today')
        return value

class UserRequestRegisterSchema(OptionalColumns):
    email: EmailStr
    password: str

class UserAddSchema(OptionalColumns):
    email: EmailStr
    hashed_password: str

class UserResponseSchema(OptionalColumns):
    email: EmailStr