from typing import Annotated

from fastapi import APIRouter, Body, Form
from pydantic import EmailStr

from internal.dependencies import DB_Dep, User_id_Dep
from internal.exceptions import (
    EmailAlreadyExists,
    EmailNotFound,
    IncorrectPassword,
    UserNotFound,
)
from internal.logger import logger_dep
from internal.schemas.auth import (
    AuthenticateUser,
    SignupResponse,
    UserPartiallyUpdate,
    UserRequestRegisterSchema,
)
from internal.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1", tags=["Authentication and JWT token"])


@router.post("/signup", summary="Create a new user", response_model=dict)
async def create_new_user(
    db: DB_Dep,
    logger: logger_dep,
    user_data: UserRequestRegisterSchema = Body(
        examples=[
            {
                "email": "example_email@example.com",
                "password": "example_password",
                "birthday": "2000-01-31",
                "fullname": "Vlad Tornikov",
            }
        ]
    ),
) -> dict:  # noqa: B008
    try:
        user: SignupResponse = await AuthService(db).create_new_user(user_data)
    except EmailAlreadyExists as e:
        raise e
    logger.info("User signed up, user_id: %s, user_email: %s", user.id, user.email)
    return {"status": "ok", "data": user}


@router.post("/signin", summary="Signin user", response_model=dict)
async def authenticate_user(
    db: DB_Dep,
    logger: logger_dep,
    username: Annotated[EmailStr, Form()],
    password: Annotated[str, Form()],
) -> dict:
    try:
        access_token: str = await AuthService(db).auth_user(
            AuthenticateUser(email=username, password=password)
        )
    except EmailNotFound as e:
        raise e
    except IncorrectPassword as e:
        raise e

    logger.info("User authenticated, received JWT token")
    return {"status": "OK", "access_token": access_token, "token_type": "Bearer"}


@router.post(
    "/verify",
    summary="Get information about authenticated user",
    response_model=SignupResponse,
)
async def get_auth_user_info(db: DB_Dep, logger: logger_dep, user_id: User_id_Dep):
    user: SignupResponse = await AuthService(db).get_data_about_user(user_id)
    logger.info("Get data about the user")
    return user


@router.patch(path="/users", summary="Update user data", response_model=SignupResponse)
async def update_user(
    db: DB_Dep,
    logger: logger_dep,
    user_id: User_id_Dep,
    updated_data: UserPartiallyUpdate,
):
    try:
        result: SignupResponse = await AuthService(db).partially_update_user(
            updated_data, user_id
        )

    except UserNotFound as e:
        raise e

    except EmailAlreadyExists as e:
        raise e

    logger.info("Successfully updated data about user")
    return result
