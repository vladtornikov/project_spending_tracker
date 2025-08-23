from datetime import date
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator
from pydantic_core import PydanticCustomError


class OptionalColumns(BaseModel):
	fullname: Optional[str] = None
	birthday: Optional[date] = None

	@field_validator("birthday", mode="before")
	@classmethod
	def check_data(cls, value: Optional[str | date]) -> Optional[date]:
		if value is None or isinstance(value, date):
			return value
		else:
			try:
				data_value = date.fromisoformat(value)
			except ValueError:
				raise PydanticCustomError(
					"birthday_invalid_format",
					"Неверная дата. Проверьте саму дату или ее формат: YYYY-MM-DD, например: 2000-01-31",
				)
			if data_value > date.today():
				raise PydanticCustomError(
					"birthday_in_future", "Дата рождения не может быть в будущем"
				)
			return data_value


class UserRequestRegisterSchema(OptionalColumns):
	email: EmailStr
	password: str


class UserAddSchema(OptionalColumns):
	email: EmailStr
	hashed_password: str


class SignupResponse(OptionalColumns):
	id: int
	email: EmailStr = None


class AuthenticateUser(BaseModel):
	email: EmailStr
	password: str


class UserResponseSchemaWithHashedPassword(BaseModel):
	id: int
	email: EmailStr
	hashed_password: str
