from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core.db import get_db_session
from app.core.security import decode_jwt_token
from app.domain.exceptions.auth import AccessTokenRequired, RefreshTokenRequired
from app.models.user import User
from app.services.user_service import UserService


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True) -> None:
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> dict:
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        token_data = decode_jwt_token(credentials.credentials)

        self.verify_token_data(token_data)

        return token_data

    def verify_token_data(self, token_data: dict) -> None:
        raise NotImplementedError("Override this method in a subclass")


class AccessTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequired()


class RefreshTokenBearer(TokenBearer):
    def verify_token_data(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequired()


async def get_current_user(
    token_data: Annotated[dict, Depends(AccessTokenBearer())],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> User:
    user_service = UserService(session)
    user = await user_service.get_by_email(token_data["user"]["email"])

    if user is None:
        raise AccessTokenRequired()

    return user
