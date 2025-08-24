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

class CategoryNameExistsException(BaseException):
	detail = "Категория с таким именем уже существует"

class EmailNotFoundException(BaseException):
	detail = "Пользователь с таким email не существует"


class IncorrectPasswordException(BaseException):
	detail = "Неверный пароль"


class IncorrectTokenException(BaseException):
	detail = "Неверный токен доступа"


class TokenExpiredException(BaseException):
	detail = "Просроченный токен доступа"


class ObjectNotFoundException(BaseException):
	detail = "Объект не найден"


class CategoryNotFoundException(ObjectNotFoundException):
	detail = "Категория не найдена"


class UserNotFoundException(ObjectNotFoundException):
	detail = "Пользователь не найден"


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
	detail = "Пользователь с таким email не зарегистрирован"


class IncorrectPasswordHTTPException(BaseHTTPException):
	status_code = 403
	detail = "Неверный пароль"


class NoAccessTokenHTTPException(BaseHTTPException):
	status_code = 401
	detail = "Не предоставлен токен доступа"


class IncorrectTokenHTTPException(BaseHTTPException):
	status_code = 401
	detail = "Некорректный токен"


class ExpiredTokenHTTPException(BaseHTTPException):
	status_code = 401
	detail = "Просроченный токен"


class CategoryNotFoundHTTPException(BaseHTTPException):
	status_code = 404
	detail = "Категория не найдена, проверьте правильность category_id и user_id"


class UserNotFoundHTTPException(BaseHTTPException):
	status_code = 404
	detail = "Пользователь не найден, проверьте правильность введеных данных"

class CategoryNameExistsHTTPException(BaseHTTPException):
	status_code = 409
	detail = "Категория с таким именем уже существует"
