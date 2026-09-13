from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.domain.exceptions.auth import ExpiredToken, InvalidToken
from app.settings import APP_SETTINGS

password_hasher = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    return password_hasher.verify(password, password_hash)


def create_jwt_token(
    user_data: dict,
    expiry: timedelta,
    refresh: bool = False,
) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "user": user_data,
        "iat": now,
        "exp": now + expiry,
        "refresh": refresh,
    }

    return jwt.encode(
        payload,
        APP_SETTINGS.JWT_SECRET,
        algorithm=APP_SETTINGS.JWT_ALGORITHM,
    )


def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            APP_SETTINGS.JWT_SECRET,
            algorithms=[APP_SETTINGS.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError as exc:
        raise ExpiredToken() from exc
    except jwt.PyJWTError as exc:
        raise InvalidToken() from exc
