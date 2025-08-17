from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from passlib.context import CryptContext

from internal.exceptions import (
	EmailNotFoundException,
	IncorrectPasswordException,
	ObjectAlreadyExistsException,
	ObjectNotFoundException,
	UserAlreadyExistsException,
)
from internal.schemas.auth import (
	AuthenticateUser,
	SignupResponse,
	UserAddSchema,
	UserRequestRegisterSchema,
	UserResponseSchemaWithHashedPassword,
)

from ..config import settings
from .base_service import BaseService


class AuthService(BaseService):
	pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

	def get_password_hash(self, password: str) -> str:
		return self.pwd_context.hash(password)

	def verify_password(self, plain_password: str, hashed_password: str) -> bool:
		return self.pwd_context.verify(plain_password, hashed_password)

	@staticmethod
	def create_access_token(
		payload_data: dict, expires_delta: Optional[timedelta] = None
	) -> str:
		to_encode = payload_data.copy()
		now = datetime.now(timezone.utc)
		if expires_delta:
			expire = now + expires_delta
		else:
			expire = datetime.now(timezone.utc) + timedelta(minutes=15)
		to_encode.update({"exp": expire, "iat": now})
		encoded_jwt = jwt.encode(
			to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
		)
		return encoded_jwt

	async def create_new_user(
		self, user_data: UserRequestRegisterSchema
	) -> SignupResponse:
		hashed_password = self.get_password_hash(user_data.password)
		schema_to_add = UserAddSchema(
			**user_data.model_dump(exclude={"password"}),
			hashed_password=hashed_password,
		)
		try:
			result: SignupResponse = await self.db.auth.add_to_the_database(
				schema_to_add.model_dump()
			)
		except ObjectAlreadyExistsException as ex:
			self.logger.exception(
				"Ошибка! Пользователь с такой эл. почтой %s уже существует",
				user_data.email,
			)
			raise UserAlreadyExistsException from ex
		await self.db.commit()
		return result

	async def auth_user(self, auth_data: AuthenticateUser) -> str:
		try:
			auth_user: UserResponseSchemaWithHashedPassword = (
				await self.db.auth.get_user_with_hashed_password(auth_data.email)
			)
		except ObjectNotFoundException as ex:
			raise EmailNotFoundException from ex
		if not self.verify_password(auth_data.password, auth_user.hashed_password):
			raise IncorrectPasswordException

		access_token = self.create_access_token(
			{"sub": auth_user.id, "email": auth_user.email}
		)
		return access_token
