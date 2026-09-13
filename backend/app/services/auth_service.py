from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_jwt_token, verify_password
from app.domain.enums.roles import UserRole
from app.domain.exceptions.auth import InvalidCredentials
from app.models.user import User
from app.services.user_service import UserService
from app.settings import APP_SETTINGS


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_service = UserService(session)

    async def register(
        self,
        name: str,
        email: str,
        password: str,
        role: UserRole,
    ) -> User:
        return await self._user_service.create_user(
            name=name,
            email=email,
            password=password,
            role=role,
        )

    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self._user_service.get_by_email(email)

        if user is None or not verify_password(password, user.password):
            raise InvalidCredentials()

        user_data = {"id": str(user.id), "email": user.email, "role": user.role.value}

        access_token = create_jwt_token(
            user_data=user_data,
            expiry=timedelta(seconds=APP_SETTINGS.ACCESS_TOKEN_EXPIRY),
            refresh=False,
        )
        refresh_token = create_jwt_token(
            user_data=user_data,
            expiry=timedelta(seconds=APP_SETTINGS.REFRESH_TOKEN_EXPIRY),
            refresh=True,
        )

        return access_token, refresh_token
