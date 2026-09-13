from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.domain.enums.roles import UserRole
from app.domain.exceptions.auth import EmailAlreadyExists
from app.models.user import User


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_email(self, email: str) -> User | None:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create_user(
        self,
        name: str,
        email: str,
        password: str,
        role: UserRole,
    ) -> User:
        if await self.get_by_email(email) is not None:
            raise EmailAlreadyExists()

        user = User(
            name=name,
            email=email,
            password=hash_password(password),
            role=role,
        )

        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)

        return user
