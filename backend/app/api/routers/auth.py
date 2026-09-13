from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import RefreshTokenBearer
from app.core.db import get_db_session
from app.core.security import create_jwt_token
from app.schemas.auth import AccessTokenResponse, LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services.auth_service import AuthService
from app.settings import APP_SETTINGS

router = APIRouter(tags=["Auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserResponse:
    auth_service = AuthService(session)
    user = await auth_service.register(
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
    )
    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> TokenResponse:
    auth_service = AuthService(session)
    access_token, refresh_token = await auth_service.login(
        email=payload.email,
        password=payload.password,
    )
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/refresh_token", response_model=AccessTokenResponse)
async def get_new_access_token(
    token_details: Annotated[dict, Depends(RefreshTokenBearer())],
) -> AccessTokenResponse:
    new_access_token = create_jwt_token(
        user_data=token_details["user"],
        expiry=timedelta(seconds=APP_SETTINGS.ACCESS_TOKEN_EXPIRY),
        refresh=False,
    )
    return AccessTokenResponse(access_token=new_access_token)
