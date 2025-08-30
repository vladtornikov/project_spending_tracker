from fastapi import status


class AppError(Exception):
    code: str = "app_error"
    message: str = "Ошибка"
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    www_authenticate: str | None = None


class ObjectAlreadyExists(AppError):
    code = "already_exists"
    message = "Объект уже существует"
    status_code = status.HTTP_409_CONFLICT


class UserAlreadyExists(ObjectAlreadyExists):
    code = "user_exists"
    message = "Пользователь уже существует"


class CategoryNameExists(ObjectAlreadyExists):
    code = "category_exists"
    message = "Категория с таким именем уже существует"


class ObjectNotFound(AppError):
    code = "not_found"
    message = "Объект не найден"
    status_code = status.HTTP_404_NOT_FOUND


class EmailNotFound(ObjectNotFound):
    code = "email_not_found"
    message = "Пользователь с таким email не существует"


class CategoryNotFound(ObjectNotFound):
    code = "category_not_found"
    message = "Категория не найдена"


class UserNotFound(ObjectNotFound):
    code = "user_not_found"
    message = "Пользователь не найден"


class TransactionNotFound(ObjectNotFound):
    code = "transaction_not_found"
    message = "Транзакция не найдена, проверьте правильность transaction_id и user_id"


class IncorrectPassword(AppError):
    code = "incorrect_password"
    message = "Неверный пароль"
    status_code = status.HTTP_401_UNAUTHORIZED
    www_authenticate = "Bearer"


class IncorrectToken(AppError):
    code = "incorrect_token"
    message = "Неверный токен"
    status_code = status.HTTP_401_UNAUTHORIZED
    www_authenticate = "Bearer"


class TokenExpired(AppError):
    code = "token_expired"
    message = "Просроченный токен"
    status_code = status.HTTP_401_UNAUTHORIZED
    www_authenticate = "Bearer"


class ForeignKeyException(AppError):
    code = "foreign_key_exception"
    message = "Эта категория не принадлежит этому пользователю"
    status_code = status.HTTP_409_CONFLICT


class ConflictHasTransactions(AppError):
    code = "still_has_transactions"
    message = "В категории есть транзакции, удалите их прежде чем удалять категорию"
    status_code = status.HTTP_409_CONFLICT
