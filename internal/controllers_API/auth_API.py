from fastapi import APIRouter, Body, Form, Response
from pydantic import EmailStr

from internal.dependencies import DB_Dep
from internal.exceptions import (
	EmailNotFoundException,
	EmailNotFoundHTTPException,
	IncorrectPasswordException,
	IncorrectPasswordHTTPException,
	UserAlreadyExistsException,
	UserEmailAlreadyExistsHTTPException,
)
from internal.logger import logger_dep
from internal.schemas.auth import (
	AuthenticateUser,
	SignupResponse,
	UserRequestRegisterSchema,
)
from internal.services.auth_service import AuthService

router = APIRouter(prefix="/api/v1", tags=["Authorization and authentication"])


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
		user: SignupResponse = await AuthService(db, logger).create_new_user(user_data)
	except UserAlreadyExistsException:
		raise UserEmailAlreadyExistsHTTPException
	logger.info("User signed up, user_id: %s, user_email: %s", user.id, user.email)
	return {"status": "ok", "data": user}


@router.post("/signin", summary="Authenticate user", response_model=dict)
async def authenticate_user(
	response: Response,
	db: DB_Dep,
	logger: logger_dep,
	user_email: EmailStr = Form(),
	password: str = Form(),
) -> dict:
	try:
		access_token: str = await AuthService(db, logger).auth_user(
			AuthenticateUser(email=user_email, password=password)
		)
	except EmailNotFoundException as ex:
		raise EmailNotFoundHTTPException from ex
	except IncorrectPasswordException as ex:
		raise IncorrectPasswordHTTPException from ex

	response.set_cookie("access_token", access_token)
	logger.info("User authenticated, received JWT token")
	return {"status": "OK", "access_token": access_token, "token_type": "Bearer"}
