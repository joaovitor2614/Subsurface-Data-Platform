import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.domain.enums.roles import UserRole


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    email: EmailStr
    role: UserRole
    created_at: datetime
