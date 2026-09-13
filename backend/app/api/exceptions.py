from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.domain.exceptions.auth import (
    AccessTokenRequired,
    EmailAlreadyExists,
    ExpiredToken,
    InvalidCredentials,
    InvalidToken,
    RefreshTokenRequired,
)

_EXCEPTION_STATUS_MAP: dict[type[Exception], int] = {
    InvalidCredentials: status.HTTP_401_UNAUTHORIZED,
    InvalidToken: status.HTTP_401_UNAUTHORIZED,
    ExpiredToken: status.HTTP_401_UNAUTHORIZED,
    RefreshTokenRequired: status.HTTP_401_UNAUTHORIZED,
    AccessTokenRequired: status.HTTP_401_UNAUTHORIZED,
    EmailAlreadyExists: status.HTTP_409_CONFLICT,
}


def register_exception_handlers(app: FastAPI) -> None:
    for exc_class, http_status in _EXCEPTION_STATUS_MAP.items():

        def make_handler(status_code: int):
            async def handler(request: Request, exc: Exception) -> JSONResponse:
                return JSONResponse(
                    status_code=status_code,
                    content={"detail": str(exc)},
                )

            return handler

        app.add_exception_handler(exc_class, make_handler(http_status))
