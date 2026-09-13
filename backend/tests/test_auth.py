from datetime import timedelta

import jwt
import pytest
from httpx import AsyncClient

from app.core.security import create_jwt_token, decode_jwt_token, hash_password
from app.domain.exceptions.auth import ExpiredToken, InvalidToken
from app.settings import APP_SETTINGS

REGISTER_PAYLOAD = {
    "name": "Ada Lovelace",
    "email": "ada@example.com",
    "password": "supersecret123",
    "role": "Geologist",
}


async def test_register_success(client: AsyncClient) -> None:
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == REGISTER_PAYLOAD["email"]
    assert "password" not in body


async def test_register_duplicate_email(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    response = await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 409


async def test_password_is_hashed(client: AsyncClient, db_session) -> None:
    from sqlalchemy import select

    from app.models.user import User

    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    result = await db_session.execute(select(User).where(User.email == REGISTER_PAYLOAD["email"]))
    user = result.scalar_one()

    assert user.password != REGISTER_PAYLOAD["password"]
    assert user.password.startswith("$argon2")


async def test_login_success(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )

    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert "refresh_token" in body


async def test_login_wrong_password(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)

    response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )

    assert response.status_code == 401


async def test_login_nonexistent_email(client: AsyncClient) -> None:
    response = await client.post(
        "/api/auth/login",
        json={"email": "nobody@example.com", "password": "whatever123"},
    )

    assert response.status_code == 401


async def test_valid_access_token_decodes(client: AsyncClient) -> None:
    token = create_jwt_token({"email": "x@example.com"}, timedelta(seconds=60), refresh=False)
    payload = decode_jwt_token(token)

    assert payload["refresh"] is False
    assert payload["user"]["email"] == "x@example.com"


async def test_valid_refresh_token_decodes(client: AsyncClient) -> None:
    token = create_jwt_token({"email": "x@example.com"}, timedelta(seconds=60), refresh=True)
    payload = decode_jwt_token(token)

    assert payload["refresh"] is True


async def test_expired_token_rejected() -> None:
    token = create_jwt_token({"email": "x@example.com"}, timedelta(seconds=-1), refresh=False)

    with pytest.raises(ExpiredToken):
        decode_jwt_token(token)


async def test_malformed_token_rejected() -> None:
    with pytest.raises(InvalidToken):
        decode_jwt_token("not-a-valid-jwt")


async def test_refresh_endpoint_rejects_access_token(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 401


async def test_refresh_endpoint_accepts_refresh_token(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = await client.get(
        "/api/auth/refresh_token",
        headers={"Authorization": f"Bearer {refresh_token}"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
