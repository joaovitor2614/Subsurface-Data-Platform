from datetime import datetime

from pydantic import BaseModel


class JWTPayload(BaseModel):
    user: dict
    iat: datetime
    exp: datetime
    refresh: bool
