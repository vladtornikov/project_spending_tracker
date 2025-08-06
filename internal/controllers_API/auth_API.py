from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import insert

from internal.databases import DB_Dep
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from internal.schemas.auth import UserRequestRegisterSchema, UserAddSchema, UserResponseSchema
from passlib.context import CryptContext
from internal.models_database.users import UsersModel


router = APIRouter(prefix='/api/v1', tags=['Authorization and authentication'])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post('/signup', summary='Create a new user')
async def create_new_user(db: DB_Dep, user_data: UserRequestRegisterSchema):
    hashed_password = get_password_hash(user_data.password)
    schema_to_add = UserAddSchema(**user_data.model_dump(), hashed_password=hashed_password)
    add_data_stmt = (
        insert(UsersModel).values(**schema_to_add.model_dump()).returning(UsersModel)
    )
    sql_respond = await db.execute(add_data_stmt)
    print(add_data_stmt.compile(compile_kwargs={"literal_binds": True}))
    result = sql_respond.scalar_one()
    result_1 = UserResponseSchema.model_validate(result, from_attributes=True)
    await db.commit()
    return {'status': 'ok', 'data': UserResponseSchema.model_validate(result_1, from_attributes=True)}
