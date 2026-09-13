from httpx import AsyncClient

REGISTER_PAYLOAD = {
    "name": "Grace Hopper",
    "email": "grace@example.com",
    "password": "supersecret123",
    "role": "ADMIN",
}


async def test_authenticated_user_can_access_protected_endpoint(client: AsyncClient) -> None:
    await client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    login_response = await client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == REGISTER_PAYLOAD["email"]


async def test_unauthenticated_user_is_rejected(client: AsyncClient) -> None:
    response = await client.get("/api/users/me")

    assert response.status_code in (401, 403)
