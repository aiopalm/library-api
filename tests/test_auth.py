import pytest
from httpx import AsyncClient

EMAIL = "test@mail.ru"
PASSWORD = "test-pass"

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == EMAIL
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD}
    )

    response = await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD}
    )

    response = await client.post(
        "/auth/login",
        json={"email": EMAIL, "password": PASSWORD}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post(
        "/auth/register",
        json={"email": EMAIL, "password": PASSWORD}
    )
    response = await client.post(
        "/auth/login",
        json={"email": EMAIL, "password": "another-pass"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "another@mail.ru", "password": "another-pass"}
    )
    assert response.status_code == 401
