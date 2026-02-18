from fastapi import HTTPException, status

class UserAlreadyExistsException(HTTPException):

    """Пользоватлем с таким email уже существует"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользоватлем с таким email уже существует"

        )

class InvalidCredentialsException(HTTPException):
    """Неверные учетные данные (email или пароль)"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"}
        )

class UserNotFoundException(HTTPException):
    """Пользователь не найден"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )


class TokenExpiredException(HTTPException):
    """Токен истек"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен истек",
            headers={"WWW-Authenticate": "Bearer"}
        )

class InvalidTokenException(HTTPException):
    """Невверный токен"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невверный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )