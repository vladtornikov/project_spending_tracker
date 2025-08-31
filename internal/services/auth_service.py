from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from internal.exceptions import (
    EmailAlreadyExists,
    EmailNotFound,
    IncorrectPassword,
    IncorrectToken,
    ObjectAlreadyExists,
    ObjectNotFound,
    TokenExpired,
    UserNotFound,
)
from internal.schemas.auth import (
    AuthenticateUser,
    SignupResponse,
    UserAddSchema,
    UserPartiallyUpdate,
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
    def encode_jwt(
        payload: dict,
        private_key: str = settings.jwt.private_key_path.read_text(),
        algorithm: str = settings.jwt.algorithm,
        expire_minutes: int = settings.jwt.access_token_expired_minutes,
    ):
        to_encode = payload.copy()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=expire_minutes)
        to_encode.update({"exp": expire, "iat": now})
        encoded_jwt = jwt.encode(to_encode, private_key, algorithm=algorithm)
        return encoded_jwt

    def decode_token(
        self,
        access_token: str,
        public_key: str = settings.jwt.public_key_path.read_text(),
        algorithm: str = settings.jwt.algorithm,
    ) -> dict:
        try:
            return jwt.decode(access_token, public_key, algorithms=algorithm)
        except jwt.exceptions.ExpiredSignatureError as e:
            self.logger.exception("Просроченный токен доступа")
            raise TokenExpired from e

        except jwt.exceptions.InvalidTokenError as e:
            self.logger.exception("Неверный токен доступа")
            raise IncorrectToken from e

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
                **schema_to_add.model_dump()
            )
        except ObjectAlreadyExists as ex:
            self.logger.exception(
                "Ошибка! Пользователь с такой эл. почтой %s уже существует",
                user_data.email,
            )
            raise EmailAlreadyExists from ex
        await self.db.commit()
        return result

    async def auth_user(self, auth_data: AuthenticateUser) -> str:
        try:
            auth_user: UserResponseSchemaWithHashedPassword = (
                await self.db.auth.get_user_with_hashed_password(auth_data.email)
            )
        except ObjectNotFound as ex:
            self.logger.exception(
                "Ошибка! Пользователь с такой эл. почтой %s не найден", auth_data.email
            )
            raise EmailNotFound from ex

        if not self.verify_password(auth_data.password, auth_user.hashed_password):
            self.logger.warning(
                "Ошибка! Неверный пароль для пользователя с эл. почтой %s",
                auth_data.email,
            )
            raise IncorrectPassword

        access_token = self.encode_jwt({"sub": str(auth_user.id)})
        return access_token

    async def get_data_about_user(self, user_id: int) -> SignupResponse:
        return await self.db.auth.get_one_or_none(id=user_id)

    async def partially_update_user(
        self,
        updated_data: UserPartiallyUpdate,
        user_id: int,
    ) -> SignupResponse:
        try:
            result = await self.db.auth.update_model(
                updated_data, exclude_unset=True, id=user_id
            )

        except ObjectNotFound as e:
            raise UserNotFound from e

        except ObjectAlreadyExists as e:
            self.logger.exception(
                "Ошибка! Пользователь с такой эл. почтой %s уже существует",
                updated_data.email,
            )
            raise EmailAlreadyExists from e

        await self.db.commit()
        return result
