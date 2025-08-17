from pydantic import EmailStr

from internal.exceptions import ObjectNotFoundException
from internal.models_database.users import UsersModel
from internal.repository.base_repository import BaseRepository
from internal.repository.data_mapper.data_mappers import AuthDataMapper
from internal.schemas.auth import UserResponseSchemaWithHashedPassword
from sqlalchemy import select


class AuthRepository(BaseRepository):
    model = UsersModel
    mapper = AuthDataMapper

    async def get_user_with_hashed_password(self, email: EmailStr):
        query = select(self.model).filter_by(email=email)
        self.logger.info(
            "SQL statement: %s",
			query.compile(compile_kwargs={"literal_binds": True})
        )

        result = await self.session.execute(query)
        res = result.scalar_one_or_none()
        if not res:
            self.logger.exception(
                'Не удалось найти данные в БД с таким email: %s', email
            )
            raise ObjectNotFoundException
        return UserResponseSchemaWithHashedPassword.model_validate(
			res, from_attributes=True
        )
