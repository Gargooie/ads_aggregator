class AdsAPIError(Exception):
    """Базовое исключение для ошибок API."""
    pass


class AuthenticationError(AdsAPIError):
    """Ошибка аутентификации."""
    pass


class RateLimitError(AdsAPIError):
    """Ошибка превышения лимита запросов."""
    pass


class DataNotFoundError(AdsAPIError):
    """Ошибка отсутствия данных."""
    pass


class InvalidTokenError(AuthenticationError):
    """Ошибка неверного токена."""
    pass
