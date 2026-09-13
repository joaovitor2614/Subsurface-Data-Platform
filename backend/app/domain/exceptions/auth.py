class AuthError(Exception):
    """Base class for authentication/authorization domain errors."""


class InvalidCredentials(AuthError):
    def __init__(self) -> None:
        super().__init__("Invalid email or password")


class EmailAlreadyExists(AuthError):
    def __init__(self) -> None:
        super().__init__("A user with this email already exists")


class InvalidToken(AuthError):
    def __init__(self) -> None:
        super().__init__("Token is invalid or malformed")


class ExpiredToken(AuthError):
    def __init__(self) -> None:
        super().__init__("Token has expired")


class RefreshTokenRequired(AuthError):
    def __init__(self) -> None:
        super().__init__("A refresh token is required for this endpoint")


class AccessTokenRequired(AuthError):
    def __init__(self) -> None:
        super().__init__("An access token is required for this endpoint")
