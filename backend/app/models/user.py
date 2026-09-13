from datetime import datetime

from sqlalchemy import Enum as SAEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.base import Base, utc_now
from app.domain.enums.roles import UserRole


class User(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"))
    created_at: Mapped[datetime] = mapped_column(default=utc_now)
