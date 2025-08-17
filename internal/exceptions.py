from fastapi import HTTPException


class BaseException(Exception):
	detail = "Ошибка"

	def __init__(self, *args, **kwargs):
		super().__init__(self.detail, *args, **kwargs)


class ObjectAlreadyExistsException(BaseException):
	detail = "Похожий объект уже существует"


class ObjectNotFoundException(BaseException):
	detail = "Объект не найден"


class UserAlreadyExistsException(BaseException):
	detail = "Пользователь уже существует"


class EmailNotFoundException(BaseException):
	detail = "Пользователь с таким email не существует"


class IncorrectPasswordException(BaseException):
	detail = "Неверный пароль"


class BaseHTTPException(HTTPException):
	status_code = 500
	detail = None

	def __init__(self):
		super().__init__(status_code=self.status_code, detail=self.detail)


class UserEmailAlreadyExistsHTTPException(BaseHTTPException):
	status_code = 409
	detail = "Пользователь с такой почтой уже существует"


class EmailNotFoundHTTPException(BaseHTTPException):
	status_code = 404
	detail = "Пользователь с таким email не зарегестрирован"


class IncorrectPasswordHTTPException(BaseHTTPException):
	status_code = 403
	detail = "Неверный пароль"
